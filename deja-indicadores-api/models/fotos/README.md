# Modelos de curadoria facial

No diretório `deja-indicadores-api`, execute `python scripts/install_fotos_face_models.py`.
O script baixa os arquivos da OpenCV Zoo, verifica o SHA-256 e os mantém fora do Git.
Configure `FOTOS_FACE_MODELS_DIR` se a API executar em outro diretório de trabalho.

- YuNet 2023mar: detecção facial; licença MIT no diretório do modelo da OpenCV Zoo.
- SFace 2021dec: características e similaridade facial; licença Apache 2.0 no diretório
  do modelo da OpenCV Zoo.

As sugestões dependem desses arquivos locais. Pessoas e referências existentes são
preservadas. A comparação não confirma identidades automaticamente; a curadoria
humana continua obrigatória. Antes de distribuir comercialmente os pesos SFace,
revisar a documentação de licença e a procedência dos dados de treinamento.

Fontes: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
e https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface
