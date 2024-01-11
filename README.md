# flexibilizador-service
Serviço para realização de flexibilização em casos de NEWAVE / DECOMP / DESSEM mediante o aparecimento de inviabilidades. Este serviço é fornecido por meio de uma API REST contendo uma única rota, que recebe os argumentos necessários para realizar a flexibilização de restrições para atendimento a inviabilidades que surgiram em execuções anteriores.

Atualmente é esperado que este serviço seja lançado no próprio cluster, com acesso ao sistema de arquivos onde os casos que serão processados se encontram. Além disso, cada programa pode demandar diferentes arquivos de entrada para a realização da flexibilização, que devem estar disponíveis no diretório do caso especificado, para que seja feita a leitura por parte do serviço.

## Instalação

Para realizar a instalação a partir do repositório, é recomendado criar um ambiente virtual e realizar a instalação das dependências dentro do mesmo.

```
$ git clone https://github.com/rjmalves/flexibilizador-service
$ cd flexibilizador-service
$ python3 -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

## Configuração

A configuração do serviço pode ser feita através de um arquivo de variáveis de ambiente `.env`, existente no próprio diretório de instalação. O conteúdo deste arquivo:

```
CLUSTER_ID=1
HOST="0.0.0.0"
PORT=5052
ROOT_PATH="/api/v1/rules"
```

Cada deploy do `flexibilizador-service` deve ter um atributo `CLUSTER_ID` único, para que outros serviços possam controlar atividades em clusters distintos. 

Atualmente as opções suportadas são:

|       Campo       |   Valores aceitos   |
| ----------------- | ------------------- |
| CLUSTER_ID        | `int`               |
| HOST              | `str`               |
| PORT              | `int`               |
| ROOT_PATH         | `str` (URL prefix)  |


## Uso

Para executar o programa, basta interpretar o arquivo `main.py`:

```
$ source ./venv/bin/activate
$ python main.py
```

No terminal é impresso um log de acompanhamento:

```
INFO:     Started server process [2133]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5052 (Press CTRL+C to quit)
INFO:     127.0.0.1:36872 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:36872 - "GET /openapi.json HTTP/1.1" 200 OK
```

Maiores detalhes sobre a rota disponível pode ser visto ao lançar a aplicação localmente e acessar a rota `/docs`, que possui uma página no formato [OpenAPI](https://swagger.io/specification/). Em geral, casos são referenciados por meio do seus caminhos no sistema de arquivos codificados em `base62`.


## Definição de Regra de Flexibilização

Cada restrição de cada modelo possui um tratamento padrão para flexibilização com base nas violações da mesma restrição. Todavia, este comportamento pode ser alterado para casos específicos através do fornecimento de regras específicas de flexibilização, modeladas pelo objeto `FlexibilizationRule`:

```json
    {
      "violationType": "string",
      "violationCode": 0,
      "violationAmount": 0.0,
      "violationUnit": "string",
      "constraintType": "string",
      "constraintCode": "string",
      "flexibilizationFactor": "string"
    }
```

TODO

## Definição de Resultado de Flexibilização

As respostas das flexibilizações se baseiam no objeto `FlexibilizationResult`. Dependendo da restrição que foi flexibilizada, alguns campos podem não possuir valores, pois o objeto foi definido de modo a cobrir todas as possíveis flexibilizações:

```json
    {
      "flexType": "string",
      "flexStage": 0,
      "flexCode": 0,
      "flexPatamar": "string",
      "flexLimit": "string",
      "flexSubsystem": "string",
      "flexAmount": 0
    }
```

O resultado possui as propriedades:

- `flexType`: tipo de restrição flexibilizada
- `flexStage`: estágio da restrição flexibilizada
- `flexCode`: código identificador da restrição flexibilizada
- `flexPatamar`: patamar da restrição flexibilizada (quando houver)
- `flexLimit`: limite (superior ou inferior) da restrição flexibilizada (quando houver)
- `flexSubsystem`: subsistema da restrição flexibilizada (quando houver)
- `flexAmount`: montante da restrição que foi flexibilizado

Objetos válidos para a flexibilização de algumas restrições são, para o modelo DECOMP:

1. Restrição de evaporação para uma usina

```json
    {
      "flexType": "EV",
      "flexStage": 1,
      "flexCode": 91,
      "flexPatamar": null,
      "flexLimit": null,
      "flexSubsystem": null,
      "flexAmount": null
    }
```

2. Restrição de taxa de irrigação (registro TI)

```json
    {
      "flexType": "TI",
      "flexStage": 1,
      "flexCode": 57,
      "flexPatamar": null,
      "flexLimit": null,
      "flexSubsystem": null,
      "flexAmount": 1.7
    }
```

3. Restrição de vazão (registro HQ)

```json
    {
      "flexType": "HQ",
      "flexStage": 1,
      "flexCode": 191,
      "flexPatamar": "1",
      "flexLimit": "L. INF",
      "flexSubsystem": null,
      "flexAmount": 7.66763865
    }
```

4. Restrição de energia armazenada (registro HE)

```json
    {
      "flexType": "HE",
      "flexStage": 1,
      "flexCode": 2,
      "flexPatamar": null,
      "flexLimit": "L. INF",
      "flexSubsystem": null,
      "flexAmount": 3.6359194500000003
    }
```

## Rota Fornecida pelo Serviço

A única rota fornecida pelo serviço é `POST /flex`, onde o corpo do objeto `JSON` contém o seguinte formato:

```json
{
    "id": "IgMI7zzpD0irzRysgz7ia2z2KbKEIQEpZ2GpEhUvJGvNxpMlD65iC9oeOQ4",
    "program": "DECOMP",
    "rules": [
        {
            "flexType": "string",
            "flexStage": 0,
            "flexCode": 0,
            "flexPatamar": "string",
            "flexLimit": "string",
            "flexSubsystem": "string",
            "flexAmount": 0
        }
    ]
}
```

Os campos informados são:

- `id`: o caminho para o diretório do caso codificado em `base62` 
- `program`:  nome do programa. Atualmente somente casos de `DECOMP` são suportados para flexibilização.  
- `rules`: lista (opcional) de objetos `FlexibilizaçãoRule`, descritos em uma seção anterior.
