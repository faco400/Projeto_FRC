# Relatório

**Código da Disciplina**: FGA0211<br>
**Disciplina**: Fundamentos de Rede de Computadores<br>
**Curso**: Engenharia de Software - FGA/UnB - 2021.2<br>
**Professor**: Fernando William Cruz<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 17/0115500  | Vinícius Vieira de Souza |
| 18/0030272  |  Antônio Ruan Moura |

## Introdução
Este projeto tem como objeto, permitir que os alunos compreendam a arquitetura de aplicações de rede
(segundo arquitetura TCP/IP) que envolvam gerência de diálogo. Para isso, devem construir uma
aplicação que disponibilize salas de bate-papo virtuais, nas quais os clientes podem ingressar e interagir.

## Metodologia Utilizada
- Os alunos se reuniram no dia 27 de abril para discutir a liguagem.
- No dia 29 de abril os alunos refletiram sobre quais as metas além dos requisitos solicitados seriam implementadas. Além do inicio de estudos sobre como seria implementadas
- No dia 3 de maio os alunos se reuniram para iniciar a implementação de chat de maneira simples (bate papo simples com sala única) e sequencialmente realizarem sua otimização para a utilização de múltiplas salas de bate papo.
- No dia 4 foi realizado ajustes, e tentativa de implementação extra (critografia de mensagens) e finalização do trabalho.

## Solução
O código principal esta dividido entre o modulo chat_server, client. 
O modulo chat_server ira rodar o servidor de forma local (IP: 127.0.0.1) na porta 8080. Ele possui funções administrativas mínimas como sugerido nas especificações do trabalho. Assim também como funções de gerenciamento do dialogo para tratar e receber mensagens do cliente. Também é neste modulo que são definidas as salas com suas capacidades maximas de membros

O modulo client permite a conexao com o servidor para a realização do dialogo, pois é através do servidor que o cliente ira repassar as mensagens para os demais usuário do chat por meio de um broadcast. Este modulo tambem define o identificador(apelido) que o cliente utilizara no chat.

Como extras os alunos implementaram comandos especiais. \quit para cortar a conexao do cliente com o servido, saindo da aplicação. O comand \l para listar todos os integrantes da mesma sala de chat. \kick para que o administrador expulse usuarios do chat atraves do nickname, e \ban para que o admin banir o cliente que não tera mais acesso ao chat usando o mesmo nickname.  Além disso ha um comando \help para ajudar o cliente.

## Conclusão
O projeto entregue possui diversas dos requisitos especificados implementados. Com a excessão de criação por parte do usuário das salas de bate papo (A criação ocorre diretamente no servidor). O cliente não consegue no momento realizar a troca de salas tendo de realizar um novo acesso para entrar em outra sala. O dialogo em vídeo/audio seria uma funcionalidade de melhoria assim como uma interface gráfica mais amigável para o cliente.

### Vinícius Vieira de Souza
O projeto foi bastante interessante, pois deu uma noção melhor sobre como os aplicativos de bate-papo como whatsapp, telegram entre outros possam ser realizado. Fazendo essa comparação também dá pra perceber como esse projeto poderia evoluir em questões de cominicação entre o cliente e servidor, assim também como questões de segurança. Uma melhoria que vejo que seria significante e óbvia é de utilizar por exemplo nrgok para gerar um domínio que emcaminhe as requisições feitas na internet para a maquina local. possibilitando que usuários externos a rede façam uso da aplicação.

### Antonio Ruan Moura

## Requisitos e Uso
Para executar o projeto é necessário que sua maquina possua python3:
```
sudo apt-get install python3
```
### Uso
Após clonar o repositório pela primeira vez, no diretório execute na raiz do projeto o comando:
```
pip install -r requirements.txt
```
Em seguida é necessário abrir dois terminais na raiz do projeto. O primeiro que deverá inicializar o servidor do chat através do comando:
```
python3 src/chat_server.py
```
Em sequencia é para realizar a conexao do cliente com o servidor. Ainda na raiz, execute:
```
python3 src/client.py
```
pronto a aplicação já esta rodando.

## Referências(FONTES)

- https://www.geeksforgeeks.org/simple-chat-room-using-python/ (Utilizada para ter uma base de como implementar o chat de forma simples com comunicação tcp/ip)
- Simple TCP Chat Room in Python (https://www.youtube.com/watch?v=3UOyky9sEQY&t=1235s) (Algoritmo que foi adaptado e utilizado pelos alunos no projeto para a elaboração dos modulos chat_server e client.)
