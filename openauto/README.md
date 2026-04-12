# The Pain is real

## Install Deb on Bookwork

Debs were avaliable
https://github.com/opencardev/openauto/tags
I instaled and tried to run the app, but it had missing SO files.

## Bookwork

``
| os | how | branch | issues |
| -- | -- | -- | -- |
| bookwork | docker | opencardev/openauto @ origin/main | Didnt work out the box. |
| bookwork | docker | opencardev/openauto @ origin/main | TODO : goign to try with an interactive console |
| bookwork | rootfs | AASDK @ newdev | TODO : try this ans see if this suffers the same cmake issues as buster |

## Buster

``
| os | how | issues |
| ------ | ------ | ------ |
| buster | on pi | locks up while compiling |
| buster | rootfs | A branch of main AASDK I manage to get to build along with the specive branch of protobuf and abseil. But isses were that cmake failed to Glob files and find dependencies, so everything was set manualy and explicity. Even CoPi was moaning that it was tedeaouse. trying to get main OpenAuto to build got too much. [The pain](buster-rootfs.md) |
