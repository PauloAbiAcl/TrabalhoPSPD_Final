# TrabalhoPSPD_Final

## Descrição
Este projeto implementa uma versão paralela e distribuída do famoso "Jogo da Vida" de Conway, com o objetivo de explorar o uso de diferentes tecnologias e frameworks para computação de alto desempenho e escalável. O foco principal é na aplicação de técnicas de paralelização e distribuição de carga de trabalho, utilizando bibliotecas e ferramentas como MPI, OpenMP, Spark, Kubernetes, Elasticsearch e Socket.

## O Jogo da Vida
O "Jogo da Vida" de Conway é um autômato celular que simula a evolução de um conjunto de células em uma grade bidimensional. Células podem estar vivas ou mortas, e a evolução de cada célula depende de um conjunto de regras simples baseadas nos estados dos vizinhos. Embora o conceito seja simples, simular o Jogo da Vida em grades grandes requer muita capacidade computacional, tornando-o um excelente exemplo para explorar computação paralela e distribuída.

## Integrantes do grupo
| Nome | Matrícula |
|---|---|
| Arthur de Melo | 190024950
| Eliás Yousef   | 190027088
| Erick Melo     | 190027355
| Paulo Vítor    | 190047968

## Instruções de uso
Este projeto é configurado para ser executado em um cluster local do Kubernetes utilizando o Minikube. Siga os passos abaixo para configurar e executar o projeto.

### Pré-requisitos

Certifique-se de ter os seguintes itens instalados em sua máquina:

- **Minikube**: [Instruções de instalação](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: [Instruções de instalação](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- **Docker**: Para criar imagens Docker ou utiliza-las

### Passos para rodar o projeto

### 1. Iniciar o Minikube

Primeiro, inicie o Minikube executando o comando abaixo:

```
minikube start
```

### 2. Dar o pull das imagens do Docker

```
docker pull <imagem docker>
```

### 3. Aplicar arquivos de configuração Kubernetes

Agora, aplique os arquivos de configuração YAML para criar os deployments, services, e outros recursos necessários. Navegue até o diretório onde os arquivos de configuração estão localizados e execute:

```
kubectl apply -f deployment.yaml
kubectl apply -f roles.yaml
```

### 4. Verificar o status dos pods

Verifique se os pods foram criados corretamente com o comando, isso mostrará o status dos pods, indicando se eles estão em execução ou se houve algum erro.

```
kubectl get pods
```

### 5. Expor um serviço

Se o projeto incluir um serviço que precisa ser acessado externamente, utilize o comando minikube service para expor o serviço. Por exemplo:

```
minikube service <nome_do_servico>
```


### 6. Executar o Cliente

Acessar a pasta socket:

```
cd ./socket
```

Executar o client para poder enviar as requisições para o server:

```
python cliente.py
```

### 7. Verificar Logs

Para verificar os logs do projeto, tanto para entender erros ou verificar resultados execute o comando abaixo:

```
kubectl logs -f <nome_do_pod>
```

### 8. Finalizar o Minikube

Quando terminar de usar o Minikube, você pode desligar o cluster com:

```
minikube stop
```

## Vídeo Apresentação e Relatório

- [Video da apresentação](https://youtu.be/_ipTsouHLg4) 
- [Relatório Trabalho](./Relatorio_TF_PSPD.pdf)


