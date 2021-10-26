import discord
from discord.ext import commands
import sqlite3
import os
import random
from cryptography.fernet import Fernet as f


client = commands.Bot(command_prefix= "?")

#Declaração de varíaveis de interceptação
nao = "http", "jpg", "png", "mp4", "mp3", "zip", "deb", "exe"

@client.event
async def on_ready():

    print("Bot is ready")

@client.command()
async def colocar(ctx):
    msg = (str(ctx.message.content))
    x = msg.splitlines()
    key = f.generate_key()
    t = f(key)
    with open("chaves.key","wb") as k:
        k.write(key)
    pt1 = x[1]
    pt2 = t.encrypt(x[2].encode())
    if any(word in msg for word in nao):
        await ctx.send("Não foi possível cadastrar")

    else:
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO infos(login, senha) VALUES (?,?)", (pt1, pt2,))
        conn.commit()
        conn.close()
        await ctx.send("Senha cadastrada com sucesso")

@client.command()
async def procurar(ctx):
    msg = (str(ctx.message.content))
    x = msg.splitlines()
    pc = x[1]
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    senha = cursor.execute("SELECT senha FROM infos WHERE login = ?",(pc,))
    resultado = senha[0]
    await ctx.send(resultado)

    conn.commit()
    conn.close()





@client.command()
async def ola(ctx):
    await ctx.send(f"Olá, para acessar meu guia de uso, digite '?ajuda'")

@client.command()
async def ajuda(ctx):
    await ctx.send('''Para colocar uma senha, digite '?colocar', e em seguida digite o comando shift enter para pular uma linha, na primeira linha você colocará o seu login, na segunda, sua senha. \n
Para ver suas senhas, digite '?ver', e em seguida, aperte barra de espaço e escreva o seu login. ''')

@client.command()
async def bot(ctx):
    await ctx.send(''' Sou SherLock, bot para gerenciamento de senhas o qual utiliza o cliente do Discord \n
Meu dever é garantir a segurança da sua senha e seu login, em volta à uma internet cheia de hackers e pessoas mal intencionadas \n
Todas as senhas são criptogradas com chaves de alta segurança para garantir que os dados sejam bem protegeidos \n
Aviso: Eu (e meu(s) administradores) NÃO iremos mudar ou visualizar sua senha ou login, além do mais, os dados são salvos já criptografados com uma chave de ordem aleatória \n
Por mais que seja seguro guardar suas senhas conosco, recomendados fortemente que não guarde as seguintes informações \n
    CPF\n
    CNPJ\n
    DATA DE NASCIMENTO\n
    INFORMAÇÕES DE CARTEIRA DE NASCIMENTO, IDENTIDADE OU CARTEIRA DE MOTORISTA\n
    INFORMAÇÕES ESTRITAMENTE PESSOAIS\n
Assim como há dados que irei aceitar, há dados que não irei aceitar, tais como:\n
    LINKS DA INTERNET (Para evitar que enviem imagens ou links maliciosos, como links de sites pornográficos ou de imagens inadequadas para o público geral)\n
    ARQUIVOS ARMAZENADOS NA WEB\n
Porém se você quer uma senha mais bem protegida, você pode sim colocar:\n
    CARACTERES ESPECIAIS (@,%,$,*, etc...)\n
Segundo Aviso: Este serviço é 100% GRATUITO, você não irá pagar uma mensalidade ou irá ficar restrito á um plano freemium, todos os recursos podem ser utilizados por todos usuários\n
porém uma forma de ajudar esse projeto a continuar é doando para o meu administrador, não é obrigatório, independente de você doa 1 real todos os dias para ele, ou nunca sequer pensou em doar para ele, nosso serviço continuará gratuito\n
Último aviso: Qualquer atualização que meus administradores aplicarem em mim será informada aos usúarios\n''')

@client.command()
async def dicas(ctx):
    await ctx.send('''Não se preocupe, estou aqui para dar algumas dicas \n
             1- Evite senhas simples (1234, 0123) \n
                'Vejo isso em todo o lugar, porque realmente preciso fazer isso ?'
                Não que seja estritamente necessário, porém é o mais recomendado \n
                Quando sua senha é enviada para algum servidor (exemplo: senha do instagram), ela pode ou não passar por criptografia \n
                Na maioria dos casos ela vai ser sim criptograda, mas quando não, ela basicamente pode ficar exposta em uma base de dados SQL (Base de dados de consulta estruturada, basicamente uma base de dados que pode ser consultada a partir de programação),
                além do hacker poder ter acesso a sua conta, ele pode fazer algo pior, como realizar a SQL Injection (metódo que basicamente embaralha todos os dados da tabela sql) e fazer você perder todos os seus dados.
                Se ela estiver criptografada, pode estar na criptografa em md5, um algoritmo regularmente eficiente mas que porém pode ser facilmente quebrado até por meio de ferramentas online.
                O mais seguro será se ela estiver criptografada com um token que precisa ser acessado, esse token deverá ser criptografado em sha256, por mais que seja bem seguro, ainda é recomendado que coloque uma senha forte.
            2- Como criar uma senha forte ? \n
                Colocar uma palavra-chave da qual você use com frequência e alguma série de números é uma boa ideia, sempre colcar senhas em sites diferentes também é recomendado, em relação aos caractéres especiais, algumas sites não permitem o uso desses caractéres, mas aqui você está livre para usar eles.
            3- E se eu perder minha senha ? 
                Você pode deletar ela com o comando ?deletar, para evitar problemas, coloque o login como algo mais próprio do que superficial.    
            
                
             ''')


token = "ODkyODkyNDI4MDMyNDMwMTMw.YVTg3w.wnZO74VcCMu3DUEB7Vsy923MNyk"
if __name__ == "__main__":
    client.run(token)