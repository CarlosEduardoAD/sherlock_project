'''----------------------------SHERLOCK_PROJECT------------------------------'''
# Documentação disponível na página do github ()

# Importação das bibliotecas
import multiprocessing  # Para realizar o lock e requerimento de processos
from discord.ext import commands  # Biblioteca do discord
import sqlite3  # Biblioteca do sqlite3
from cryptography.fernet import Fernet as f  # Biblioteca utilizada para a criptografia
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import re

# Declaração de variáveis/objetos principais
lock = multiprocessing.Lock()
client = commands.Bot(command_prefix="?")
nao = "http", "jpg", "png", "mp4", "mp3", "zip", "deb", "exe", "rpm","rar","sql","html","mpeg"


# Checagem de disponibilidade do bot
@client.event
async def on_ready():
    print("Bot is ready")
# Comando central de alocamento de informações do usuário
@client.command()
async def colocar(ctx):
    try:
        msg = (str(ctx.message.content)) # Divisão do input
        x = msg.splitlines()
        pt1 = str(x[1])
        pt2 = (x[2].encode("utf-8"))
        pattern = "[a-zA-Z0-9]+\.[0-9]"
        if (re.search(pattern, pt1)):
            salt = os.urandom(256)
            main_hash = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=320000,
            )
            key = (main_hash.derive(pt2)) #Geração da chave
            t = f(base64.urlsafe_b64encode(key))
            nova_senha = t.encrypt(pt2)
            if any(word in msg for word in nao):
                await ctx.send("Com licença, não posso criptografar links ou arquivos, por favor, "
                               "digite uma senha sem extensão de arquivo ou protocolo web (http)")

            else:
                lock.acquire(True)
                conn = sqlite3.connect('base.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO userinfo(login,hash,senha) VALUES (?,?,?)", (pt1, key, nova_senha,))
                conn.commit()
                conn.close()
                await ctx.send("Senha cadastrada com sucesso")
                lock.release()
        else:
            await ctx.send("Login inválido, digite ele novamente")
    except Exception:
        await ctx.send("Não foi possível cadastrar sua senha, "
                       "Para esse tipo de problema, faça esses três passos\n"
                       "1- Veja se não colocou arquivos ou links da web\n"
                       "2- Observe se preencheu os três campos corretamente (para mais informações digite ajuda)\n"
                       "3- Verifique se o seu login não é o mesmo do que o de outra pessoa\n")


@client.command(pass_context=True)
async def procurar(ctx):
    try:
        msg = (str(ctx.message.content))
        x = msg.splitlines()
        pc = str(x[1])
        lock.acquire(True)
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM userinfo WHERE login = (?)", (pc,))
        fetch = cursor.fetchone()
        senha_criptografada = fetch[0]
        cursor.execute("SELECT hash FROM userinfo WHERE login = (?)", (pc,))
        fetch2 = cursor.fetchone()
        key = fetch2[0]
        t = f(base64.urlsafe_b64encode(key))
        senha_descriptografada = t.decrypt(senha_criptografada)
        lock.release()
        await ctx.author.send("Aqui está sua senha senhor: " + senha_descriptografada.decode("utf-8"))
        conn.commit()
        conn.close()
    except Exception:
        await ctx.send('''Pelo visto o senhor não cadastrou essa senha,
    cadastre ela primeiro para que eu possa guardá-la ou procure outra que já cadastrou''')


@client.command()
async def deletar(ctx):
    try:
        lock.acquire(True)
        msg = str(ctx.message.content)
        x = msg.splitlines()
        palavra = x[1]
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM userinfo WHERE login = (?)", (palavra,))
        await ctx.send("Não foi possível achar sua senha")
        conn.commit()
        conn.close()
        lock.release()
        await ctx.send("Sua senha foi deletada com sucesso")
    except:
        await ctx.send("Não foi possível deletar, verifique se preencheu a segunda linha com seu login")

@client.command()
async def ola(ctx):
    await ctx.send(f"Olá, para acessar meu guia de uso, digite '?ajuda'")


@client.command()
async def ajuda(ctx):
    await ctx.send('''Para colocar uma senha, digite '?colocar', e em seguida digite o comando shift 
enter para pular uma linha, na primeira linha você colocará o seu login, na segunda, sua senha. \n
Para ver suas senhas, digite '?procurar', e em seguida, aperte barra de espaço e escreva o seu login. \n 
Seu login precisa ter pelomenos uma letra maíscula, é necessário colocar também um ponto e alguns números, mais ou menos assim \n 
minhasenhasecreta.201920202021 \n
não, caso contrário a base de dados pode ter conflitos na hora de buscar sua senha \n
Não é possível colocar uma senha com o mesmo login, se quiser colocar uma outra senha para o seu login, terá que ou deletar seu login antigo ou criar fazer uma nova colocação.''')


@client.command()
async def bot(ctx):
    await ctx.send(''' Sou SherLock, bot para gerenciamento de senhas o qual utiliza o cliente do Discord \n
Meu dever é garantir a segurança da sua senha e seu login, 
em volta à uma internet cheia de hackers e pessoas mal intencionadas \n
Todas as senhas são criptogradas com chaves de alta segurança para garantir que os dados sejam bem protegeidos \n
Aviso: Eu (e meu(s) administradores) NÃO iremos mudar ou visualizar sua senha ou login,
além do mais, os dados são salvos já criptografados com uma chave de ordem aleatória \n
Por mais que seja seguro guardar suas senhas conosco, recomendados fortemente que não guarde as seguintes informações \n
    CPF\n
    CNPJ\n
    DATA DE NASCIMENTO\n
    INFORMAÇÕES DE CARTEIRA DE NASCIMENTO, IDENTIDADE OU CARTEIRA DE MOTORISTA\n
    INFORMAÇÕES ESTRITAMENTE PESSOAIS\n
Assim como há dados que irei aceitar, há dados que não irei aceitar, tais como:\n
    LINKS DA INTERNET (Para evitar que enviem imagens ou links maliciosos, 
    como links de sites pornográficos ou de imagens inadequadas para o público geral)\n
    ARQUIVOS ARMAZENADOS NA WEB\n
Porém se você quer uma senha mais bem protegida, você pode sim colocar:\n
    CARACTERES ESPECIAIS (@,%,$,*, etc...)\n
Segundo Aviso: Este serviço é 100% GRATUITO, você não irá pagar uma mensalidade ou irá ficar restrito á um plano freemium, 
todos os recursos podem ser utilizados por todos usuários\n
porém uma forma de ajudar esse projeto a continuar é doando para o meu administrador, 
não é obrigatório, independente de você doa 1 real todos os dias para ele, 
ou nunca sequer pensou em doar para ele, nosso serviço continuará gratuito\n
Último aviso: Qualquer atualização que meus administradores aplicarem em mim será informada aos usúarios\n''')

@client.command()
async def dicas(ctx):
    await ctx.send('''Não se preocupe, estou aqui para dar algumas dicas \n
             1- Evite senhas simples (1234, 0123) \n
                'Vejo isso em todo o lugar, porque realmente preciso fazer isso ?'
                Não que seja estritamente necessário, porém é o mais recomendado \n
                Quando sua senha é enviada para algum servidor (exemplo: senha do instagram), 
                ela pode ou não passar por criptografia \n
                Na maioria dos casos ela vai ser sim criptograda, mas quando não,
                ela basicamente pode ficar exposta em uma base de dados SQL 
                (Base de dados de consulta estruturada, basicamente uma base de dados que pode ser consultada a partir de programação),
                além do hacker poder ter acesso a sua conta, ele pode fazer algo pior, 
                como realizar a SQL Injection (metódo que basicamente embaralha todos os dados da tabela sql) e fazer você perder todos os seus dados.
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