import telebot
import random
import string

# Configurações iniciais
TOKEN = '8739811212:AAGb5wSFahquYCe57q4QPmJ0Q5ESUEoBCNU'
ADMIN_ID = 8040896124  # COLOQUE SEU ID DO TELEGRAM AQUI

bot = telebot.TeleBot(TOKEN)

# Dicionário para armazenar as keys e seu status
banco_keys = {}

def gerar_codigo():
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=12))
    return f"KEY-{codigo[:4]}-{codigo[4:8]}-{codigo[8:]}"


# --- COMANDO DE ENTRADA (MENSAGEM DE BOAS-VINDAS) ---

@bot.message_handler(commands=['start'])
def enviar_welcome(message):
    # Se for você (admin) abrindo o bot
    if message.from_user.id == ADMIN_ID:
        texto_admin = (
            "👋 Olá, Administrador!\n\n"
            "• Use `/gerar` para criar novas chaves.\n"
            "• Use `/painel` para ver o status das chaves."
        )
        bot.reply_to(message, texto_admin, parse_mode='Markdown')
        return

    # Se for um cliente/usuário comum
    texto_cliente = "👋 Olá! Por favor, **envie a sua Key de ativação** aqui abaixo para liberar seu acesso:"
    
    # Envia a mensagem e diz ao bot para "esperar" a resposta do usuário na função 'processar_key'
    msg = bot.reply_to(message, texto_cliente, parse_mode='Markdown')
    bot.register_next_step_handler(msg, processar_key)


# --- FUNÇÃO QUE VALIDA A KEY ENVIADA ---

def processar_key(message):
    key_enviada = message.text.strip()

    # Se o usuário tentar usar outro comando em vez de mandar a key
    if key_enviada.startswith('/'):
        bot.reply_to(message, "❌ Operação cancelada. Se quiser tentar novamente, digite /start")
        return

    # 1. Verifica se a key existe no sistema
    if key_enviada not in banco_keys:
        msg = bot.reply_to(message, "❌ **Key inválida ou incorreta!**\n\nPor favor, digite a key correta novamente:")
        bot.register_next_step_handler(msg, processar_key) # Dá outra chance para digitar sem fechar o fluxo
        return
        
    # 2. Verifica se a key já foi usada
    if banco_keys[key_enviada] != "Disponível":
        bot.reply_to(message, "⚠️ **Esta key já foi utilizada por outro usuário.**\nSolicite uma nova key com o vendedor.")
        return
        
    # 3. Sucesso: Ativa a key e vincula ao ID do cliente
    banco_keys[key_enviada] = f"Resgatada por {message.from_user.id}"
    
    # Mensagem de sucesso para o cliente
    bot.reply_to(message, f"✅ **Key resgatada com sucesso!**\nObrigado pela compra. Seu acesso foi liberado!", parse_mode='Markdown')
    
    # Notificação secreta para você (o dono)
    bot.send_message(ADMIN_ID, f"🔔 **Notificação de Venda:**\nO usuário `{message.from_user.first_name}` (ID: `{message.from_user.id}`) acabou de resgatar a key `{key_enviada}`.", parse_mode='Markdown')


# --- COMANDOS DO ADMINISTRADOR (APENAS VOCÊ) ---

@bot.message_handler(commands=['gerar'])
def gerar_key(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Você não tem permissão para gerar keys.")
        return

    nova_key = gerar_codigo()
    banco_keys[nova_key] = "Disponível"
    
    bot.reply_to(message, f"🔑 **Nova key gerada para venda:**\n\n`{nova_key}`", parse_mode='Markdown')

@bot.message_handler(commands=['painel'])
def painel_admin(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Acesso negado.")
        return
    
    if not banco_keys:
        bot.reply_to(message, "Nenhuma key cadastrada no sistema.")
        return
        
    texto = "📋 **Status de todas as Keys:**\n\n"
    for key, status in banco_keys.items():
        texto += f"• `{key}`: {status}\n"
    
    bot.reply_to(message, texto, parse_mode='Markdown')

print("Bot de Vendas Atualizado iniciado...")
bot.polling()
