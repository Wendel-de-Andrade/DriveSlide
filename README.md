# DriveSlide

Aplicação desktop em Python que transforma uma pasta do Google Drive em um slideshow fullscreen sincronizado automaticamente.

## Visão geral

O DriveSlide foi criado para exibir imagens armazenadas no Google Drive sem exigir atualização manual da apresentação. O aplicativo autentica no Drive, baixa as imagens para um diretório temporário, monitora alterações na pasta e atualiza o slideshow em segundo plano.

## Principais funcionalidades

- Autenticação com Google Drive via PyDrive
- Download automático de imagens de uma pasta informada pelo usuário
- Sincronização periódica para detectar novos arquivos e remoções
- Slideshow fullscreen com redimensionamento proporcional das imagens
- Thread separada para atualização dos arquivos sem bloquear a interface
- Diretório temporário com limpeza automática no encerramento
- Persistência das últimas configurações utilizadas
- Interface desktop com CustomTkinter
- Atalho `ESC` para sair do modo fullscreen

## Stack

- Python
- PyDrive
- Tkinter / CustomTkinter
- Pillow
- Threading
- Keyboard

## Como funciona

1. O usuário informa o ID da pasta no Google Drive.
2. Define o intervalo de verificação da pasta e o tempo entre slides.
3. O aplicativo autentica no Google Drive e baixa as imagens disponíveis.
4. O slideshow é aberto em fullscreen.
5. Uma thread monitora periodicamente a pasta no Drive e sincroniza inclusões e exclusões.

## Execução

Instale as dependências do projeto e configure as credenciais necessárias para autenticação do PyDrive/Google Drive.

Depois execute:

```bash
python main.py
```

Na interface, informe o ID da pasta, o intervalo de verificação e o tempo de exibição de cada imagem.

## Decisões técnicas

A verificação do Google Drive roda em uma thread separada para evitar que a sincronização de arquivos interrompa a troca de slides ou congele a interface. As imagens são armazenadas apenas em diretório temporário durante a execução e removidas ao encerrar o programa.

## Próximos passos

- Migrar a integração para a API atual do Google Drive
- Adicionar tratamento estruturado de logs
- Criar arquivo de dependências e configuração de ambiente
- Adicionar testes para funções de sincronização e configuração
- Empacotar uma versão distribuível para Windows

## Licença

MIT
