# cocada-web
 
Contact database built based on analyses of the COCADA tool on data collected from the Protein Data Base (PDB).

## update 2025
COCADA-WEB and COCADA-DB were merged.

# CodeIgniter 4 Application Starter

## What is CodeIgniter?

CodeIgniter is a PHP full-stack web framework that is light, fast, flexible and secure.
More information can be found at the [official site](https://codeigniter.com).

## Installation & updates

`composer create-project codeigniter4/appstarter` then `composer update` whenever
there is a new release of the framework.

When updating, check the release notes to see if there are any changes you might need to apply
to your `app` folder. The affected files can be copied or merged from
`vendor/codeigniter4/framework/app`.

## Setup

Copy `env` to `.env` and tailor for your app, specifically the baseURL
and any database settings.

## Important Change with index.php

`index.php` is no longer in the root of the project! It has been moved inside the *public* folder,
for better security and separation of components.

This means that you should configure your web server to "point" to your project's *public* folder, and
not to the project root. A better practice would be to configure a virtual host to point there. A poor practice would be to point your web server to the project root and expect to enter *public/...*, as the rest of your logic and the
framework are exposed.

**Please** read the user guide for a better explanation of how CI4 works!

## Server Requirements

PHP version 8.1 or higher is required, with the following extensions installed:

Additionally, make sure that the following extensions are enabled in your PHP:

- json (enabled by default - don't turn it off)
- [mysqlnd](http://php.net/manual/en/mysqlnd.install.php) if you plan to use MySQL
- [libcurl](http://php.net/manual/en/curl.requirements.php) if you plan to use the HTTP\CURLRequest library


# Documentação PT-BR

## Colocando em produção (Apache Server)
No terminal, acesse o diretório raiz do Apache: 
    cd /var/www/html

Clone o repositório: 
    git clone https://github.com/LBS-UFMG/rnapedia.git

Acesse o novo diretório criado:
    cd rnapedia

Instale as bibliotecas usando composer:
    composer install

Mude o dono do diretório para o apache:
    sudo chown -R www-data:www-data *

Caso necessário, apague o cache na pasta /writable/cache
    cd writable/cache
    rm -rf *

Agora vamos configurar o ambiente. Volte para a raiz do projeto e faça uma cópia de env:
    cd /var/www/html/rnapedia
    cp env .env

Agora edite o arquivo .env:
    nano .env

Remova o comentário das linhas:
    CI_ENVIRONMENT = production
    app.baseURL = 'http://bioinfo.dcc.ufmg.br/rnapedia/index.php'

ctrl+o e ctrl+x



Confira se o site está configurado no Apache
    sudo nano /etc/apache2/sites-available/000-default.conf

Agora veja se a existe a seguinte linha (pressione ctrl+w e digite 'rnapedia'):
    Alias /rnapedia /var/www/html/rnapedia/public

Se não existir, adicione a linha e salve o arquivo com ctrl+o. Pressione ctrl+x para sair.

Depois reinicie o apache com o comando:
    sudo service apache2 restart


## Sobre os dados

A pasta `/public/data` não é sincronizada pelo GitHub. Nela há duas pastas: `pdb` e `projects`. A pasta `pdb` contém os arquivos de contatos calculados pelo COCADA-CLI. A pasta `projects` contém dados calculados pela interface web.

