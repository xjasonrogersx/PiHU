#include <alsa/asoundlib.h>

#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>

extern "C" {
#include <libavcodec/avcodec.h>
#include <libavutil/channel_layout.h>
#include <libavutil/mathematics.h>
#include <libavutil/samplefmt.h>
#include <libswresample/swresample.h>
}

#include "dabplus_decoder.h"
#include "raon_tuner.h"

class DabLatmPlayer {
 public:
  DabLatmPlayer() {
    decoder_ = avcodec_find_decoder(AV_CODEC_ID_AAC_LATM);
    if (!decoder_) {
      throw std::runtime_error("Failed to find AAC LATM decoder");
    }

    codec_ctx_ = avcodec_alloc_context3(decoder_);
    packet_ = av_packet_alloc();
    frame_ = av_frame_alloc();
    if (!codec_ctx_ || !packet_ || !frame_) {
      throw std::runtime_error("Failed to allocate FFmpeg decode structures");
    }

    if (avcodec_open2(codec_ctx_, decoder_, nullptr) < 0) {
      throw std::runtime_error("Failed to open AAC LATM decoder");
    }
  }

  ~DabLatmPlayer() {
    if (pcm_) snd_pcm_close(pcm_);
    if (swr_) swr_free(&swr_);
    if (frame_) av_frame_free(&frame_);
    if (packet_) av_packet_free(&packet_);
    if (codec_ctx_) avcodec_free_context(&codec_ctx_);
  }

  void decodeAndPlay(const std::vector<uint8_t>& latmFrame) {
    if (latmFrame.empty()) {
      return;
    }

    av_packet_unref(packet_);
    if (av_new_packet(packet_, static_cast<int>(latmFrame.size())) < 0) {
      return;
    }
    std::memcpy(packet_->data, latmFrame.data(), latmFrame.size());

    const int sendRet = avcodec_send_packet(codec_ctx_, packet_);
    if (sendRet < 0) {
      return;
    }

    while (true) {
      const int recvRet = avcodec_receive_frame(codec_ctx_, frame_);
      if (recvRet == AVERROR(EAGAIN) || recvRet == AVERROR_EOF) {
        break;
      }
      if (recvRet < 0) {
        break;
      }
      if (!prepareOutputForFrame(frame_)) {
        continue;
      }
      playDecodedFrame(frame_);
    }
  }

 private:
  bool prepareOutputForFrame(const AVFrame* frame) {
    const int inSampleRate = frame->sample_rate;
    const int inChannels = frame->channels;
    const AVSampleFormat inFmt = static_cast<AVSampleFormat>(frame->format);

    if (inSampleRate <= 0 || inChannels <= 0) {
      return false;
    }

    const uint64_t inLayout =
        frame->channel_layout ? frame->channel_layout
                              : av_get_default_channel_layout(inChannels);

    if (!swr_ || inSampleRate != input_sample_rate_ || inChannels != channels_ ||
        inFmt != input_sample_fmt_) {
      if (swr_) swr_free(&swr_);

      swr_ = swr_alloc_set_opts(nullptr, inLayout, AV_SAMPLE_FMT_S16, inSampleRate,
                                inLayout, inFmt, inSampleRate, 0, nullptr);
      if (!swr_ || swr_init(swr_) < 0) {
        if (swr_) swr_free(&swr_);
        return false;
      }

      if (!setupAlsa(inSampleRate, inChannels)) {
        return false;
      }

      input_sample_rate_ = inSampleRate;
      input_sample_fmt_ = inFmt;
      channels_ = inChannels;
    }

    return true;
  }

  bool setupAlsa(int sampleRate, int channels) {
    if (pcm_) {
      snd_pcm_drain(pcm_);
      snd_pcm_close(pcm_);
      pcm_ = nullptr;
    }

    if (snd_pcm_open(&pcm_, "default", SND_PCM_STREAM_PLAYBACK, 0) < 0) {
      std::cerr << "Failed to open ALSA device\n";
      return false;
    }

    snd_pcm_hw_params_t* params = nullptr;
    snd_pcm_hw_params_alloca(&params);
    if (snd_pcm_hw_params_any(pcm_, params) < 0 ||
        snd_pcm_hw_params_set_access(pcm_, params, SND_PCM_ACCESS_RW_INTERLEAVED) < 0 ||
        snd_pcm_hw_params_set_format(pcm_, params, SND_PCM_FORMAT_S16_LE) < 0 ||
        snd_pcm_hw_params_set_channels(pcm_, params, channels) < 0) {
      std::cerr << "Failed to set ALSA hardware params\n";
      snd_pcm_close(pcm_);
      pcm_ = nullptr;
      return false;
    }

    unsigned int alsaRate = static_cast<unsigned int>(sampleRate);
    if (snd_pcm_hw_params_set_rate_near(pcm_, params, &alsaRate, nullptr) < 0 ||
        snd_pcm_hw_params(pcm_, params) < 0 || snd_pcm_prepare(pcm_) < 0) {
      std::cerr << "Failed to apply ALSA hardware params\n";
      snd_pcm_close(pcm_);
      pcm_ = nullptr;
      return false;
    }
    return true;
  }

  bool recoverAlsa(int err) {
    if (err == -EPIPE) {
      return snd_pcm_prepare(pcm_) >= 0;
    }
    if (err == -ESTRPIPE) {
      while ((err = snd_pcm_resume(pcm_)) == -EAGAIN) {
      }
      if (err < 0) {
        return snd_pcm_prepare(pcm_) >= 0;
      }
      return true;
    }
    return snd_pcm_recover(pcm_, err, 1) >= 0;
  }

  void playDecodedFrame(const AVFrame* frame) {
    const int maxOutSamples =
        av_rescale_rnd(swr_get_delay(swr_, frame->sample_rate) + frame->nb_samples,
                       frame->sample_rate, frame->sample_rate, AV_ROUND_UP);
    out_buffer_.resize(static_cast<size_t>(maxOutSamples) * channels_ *
                       sizeof(int16_t));
    uint8_t* outData = out_buffer_.data();
    const int outSamples =
        swr_convert(swr_, &outData, maxOutSamples,
                    const_cast<const uint8_t**>(frame->extended_data),
                    frame->nb_samples);
    if (outSamples <= 0) {
      return;
    }

    int totalFrames = outSamples;
    int16_t* pcmData = reinterpret_cast<int16_t*>(out_buffer_.data());
    int writtenFrames = 0;
    while (writtenFrames < totalFrames) {
      const snd_pcm_sframes_t ret =
          snd_pcm_writei(pcm_, pcmData + (writtenFrames * channels_),
                         totalFrames - writtenFrames);
      if (ret < 0) {
        if (!recoverAlsa(static_cast<int>(ret))) {
          return;
        }
        continue;
      }
      writtenFrames += static_cast<int>(ret);
    }
  }

  const AVCodec* decoder_{nullptr};
  AVCodecContext* codec_ctx_{nullptr};
  AVPacket* packet_{nullptr};
  AVFrame* frame_{nullptr};
  SwrContext* swr_{nullptr};
  snd_pcm_t* pcm_{nullptr};
  int input_sample_rate_{0};
  int channels_{0};
  AVSampleFormat input_sample_fmt_{AV_SAMPLE_FMT_NONE};
  std::vector<uint8_t> out_buffer_;
};

DabPlusServiceComponentDecoder* dabplus_decoder = nullptr;
DabLatmPlayer* dab_player = nullptr;

class CoutMscObserver : public MscObserver {
  void mscData(const std::vector<uint8_t>& data) {
    dabplus_decoder->componentDataInput(data, false);
  }
};

void usage() {
  std::cout << "Usage: dab_play frequency subchannel bitrate\n"
               "Examples: \n\n"
               "  dab_play 222064000 17 40 # Tune in to Capital XTRA\n"
               "\n"
               "Arguments:\n"
               "  frequency\n"
               "     The dab frequency to tune in to in Hz. e.g 225648000\n"
               "  subchannel\n"
               "     The subchannel on the frequency to receive\n"
               "  bitrate\n"
               "     The bitrate dab+ stream\n"
               "\n";
}

int main(int argc, char* argv[]) {
  if (argc != 4) {
    usage();
    return EXIT_FAILURE;
  }

  RaonTunerInput* tuner = new RaonTunerInput();
  CoutMscObserver* mscObserver = new CoutMscObserver();
  dabplus_decoder = new DabPlusServiceComponentDecoder();
  dabplus_decoder->setSubchannelBitrate(atoi(argv[3]));

  try {
    dab_player = new DabLatmPlayer();
  } catch (const std::exception& ex) {
    std::cerr << "Audio decoder init failed: " << ex.what() << "\n";
    return EXIT_FAILURE;
  }

  dabplus_decoder->setLatmDataCallback([](const std::vector<uint8_t>& latmFrame) {
    dab_player->decodeAndPlay(latmFrame);
  });

  tuner->initialize();
  tuner->tuneFrequency(atoi(argv[1]));
  tuner->openSubChannel(atoi(argv[2]));
  tuner->setMscObserver(mscObserver);

  while (1) {
    tuner->readData();
  }

  delete tuner;
  delete dabplus_decoder;
  delete dab_player;
  return EXIT_SUCCESS;
}
