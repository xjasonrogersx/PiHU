#include <mosquitto.h>

#include <cstring>
#include <iostream>
#include <nlohmann/json.hpp>

#include "dabplus_decoder.h"
#include "raon_tuner.h"

using json = nlohmann::json;

DabPlusServiceComponentDecoder* dabplus_decoder;
RaonTunerInput* tuner;
struct mosquitto* mosq = nullptr;

class CoutMscObserver : public MscObserver {
  void mscData(const std::vector<uint8_t>& data) {
    dabplus_decoder->componentDataInput(data, false);
  }
};

void on_connect(struct mosquitto* mosq, void* obj, int reason_code) {
  if (reason_code != 0) {
    std::cerr << "Connect failed with code " << reason_code << std::endl;
    return;
  }
  std::cout << "Connected to MQTT broker" << std::endl;

  // Subscribe to tune commands
  mosquitto_subscribe(mosq, nullptr, "car/dab/tune_to", 1);
}

void on_message(struct mosquitto* mosq, void* obj,
                const struct mosquitto_message* msg) {
  if (msg->payloadlen == 0) {
    return;
  }

  std::string payload(static_cast<char*>(msg->payload), msg->payloadlen);
  std::string topic(msg->topic);

  try {
    if (topic == "car/dab/tune_to") {
      auto data = json::parse(payload);

      uint32_t frequency = data.value("frequency", 0);
      uint8_t subchannel = data.value("subchannel", 0);
      uint8_t bitrate = data.value("bitrate", 64);

      if (frequency > 0) {
        std::cout << "Tuning to frequency: " << frequency
                  << ", subchannel: " << (int)subchannel
                  << ", bitrate: " << (int)bitrate << std::endl;

        tuner->tuneFrequency(frequency);
        tuner->openSubChannel(subchannel);
        dabplus_decoder->setSubchannelBitrate(bitrate);
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "Error parsing MQTT message: " << e.what() << std::endl;
  }
}

int main(int argc, char* argv[]) {
  const char* host = "localhost";
  int port = 1883;

  if (argc > 1) {
    host = argv[1];
  }
  if (argc > 2) {
    port = atoi(argv[2]);
  }

  // Initialize MQTT
  mosquitto_lib_init();

  mosq = mosquitto_new(nullptr, true, nullptr);
  if (!mosq) {
    std::cerr << "Failed to create mosquitto instance" << std::endl;
    return EXIT_FAILURE;
  }

  mosquitto_connect_callback_set(mosq, on_connect);
  mosquitto_message_callback_set(mosq, on_message);

  int rc = mosquitto_connect(mosq, host, port, 60);
  if (rc != MOSQ_ERR_SUCCESS) {
    std::cerr << "Failed to connect to MQTT broker at " << host << ":" << port
              << std::endl;
    mosquitto_destroy(mosq);
    mosquitto_lib_cleanup();
    return EXIT_FAILURE;
  }

  // Initialize tuner
  try {
    tuner = new RaonTunerInput();
    CoutMscObserver* mscObserver = new CoutMscObserver();
    dabplus_decoder = new DabPlusServiceComponentDecoder();
    dabplus_decoder->setSubchannelBitrate(64);

    tuner->initialize();
    tuner->setMscObserver(mscObserver);

    std::cout << "DAB tuner AAC with MQTT control started" << std::endl;
    std::cout << "Listening for tune commands on car/dab/tune_to" << std::endl;

    // Main loop
    while (1) {
      mosquitto_loop(mosq, 100, 1);
      tuner->readData();
    }

    delete tuner;
    mosquitto_destroy(mosq);
    mosquitto_lib_cleanup();

  } catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << std::endl;
    return EXIT_FAILURE;
  }

  return 0;
}
