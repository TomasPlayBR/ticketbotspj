from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import Intents
from flask import Flask
from threading import Thread
import discord

app = Flask('')

@app.route('/')
def home():
    return "Bot está online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    send_panel.start()  # Iniciar a tarefa de envio do painel

    # Criação do painel
    embed = discord.Embed(title="PJ | Sistema de Tickets", 
                          description="Bem-vindo ao nosso sistema de tickets. Clique na opção que mais se adequa ao seu problema.",
                          color=discord.Color.blue())

    embed.add_field(name="Como abrir um ticket", value="• Clica no botão abaixo para abrir um ticket.\n• Um canal privado será criado para ti.\n• A nossa equipa irá responder rapidamente.", inline=False)
    embed.add_field(name="Motivos para abrir um ticket:", value="• Esclarecer dúvidas.\n• Para denunciar um membro da PJ\n• Para entrar na PJ \n• Qualquer outra questão.", inline=False)
    embed.set_image(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQu-dhIkHzQmolUan7-Hsg_nh11UVaAe81AQ&s")

    # Criação dos 4 botões
    button1 = Button(label="Dúvidas", style=discord.ButtonStyle.blurple)
    button2 = Button(label="Denuncias", style=discord.ButtonStyle.green)
    button3 = Button(label="Recrutamento privado", style=discord.ButtonStyle.gray)
    button4 = Button(label="Outras Questões", style=discord.ButtonStyle.red)

    # Atribuir funções de criação de canais
    button1.callback = lambda interaction: open_ticket(interaction, "Dúvidas")
    button2.callback = lambda interaction: open_ticket(interaction, "Denuncias")
    button3.callback = lambda interaction: open_ticket(interaction, "Recrutamento privado")
    button4.callback = lambda interaction: open_ticket(interaction, "Outras Questões")

    view = View()
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)

    # Enviar o painel e guardar a mensagem
    bot.current_message = await channel.send(embed=embed, view=view)

async def verificar_cargo(interaction):
    cargo = interaction.guild.get_role(1146444299093946435)  # ID do cargo
    return cargo in interaction.user.roles

async def open_ticket(interaction, motivo):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="Tickets")
    ticket_channel = await guild.create_text_channel(f"📂{interaction.user.name}-{motivo}", category=category)

    # Abaixo da criação do canal
    role = guild.get_role(1146444299093946435)  # ID do cargo
    if role:
        await ticket_channel.send(f"{role.mention} Um novo ticket foi aberto por {interaction.user.mention}.")

    # Configurar permissões para o usuário que abriu o ticket
    await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

    # Criar painel de controle no canal do ticket
    embed = discord.Embed(title="Sistema de Ticket | Polícia Judiciária | SRP", 
                          description=f"Olá, {interaction.user.mention}. Seja bem-vindo ao nosso atendimento.\n\n📜**Motivo:** {motivo}",
                          color=discord.Color.green())

    embed.set_footer(text=f"Sistema de ticket da PJ - {interaction.created_at.strftime('%d/%m/%Y')}")
    embed.set_thumbnail(url=interaction.user.avatar.url)

    # Interação
    await interaction.response.defer()

    # Botões para assumir e fechar o ticket
    button_assumir = Button(label="✅ Assumir", style=discord.ButtonStyle.green)
    button_assumir.callback = lambda inter: assumir_ticket(inter, interaction.user, ticket_channel)

    button_painel_staff = Button(label="🛠️ Painel", style=discord.ButtonStyle.blurple)
    button_painel_staff.callback = lambda inter: painel_staff(inter)

    button_fechar = Button(label="🔑 Fechar", style=discord.ButtonStyle.red)
    button_fechar.callback = lambda inter: fechar_ticket(inter, interaction.user, ticket_channel)

    # Novo botão para fase 1
    button_recrutamento = Button(label="📄 Fase 1", style=discord.ButtonStyle.blurple)
    button_recrutamento.callback = lambda inter: Recrutamento(inter, interaction.user)

    # Botões para fases 2 e 3
    button_fase2 = Button(label="📄 Fase 2", style=discord.ButtonStyle.blurple)
    button_fase2.callback = lambda inter: fase_2(inter, interaction.user)

    button_fase3 = Button(label="📄 Fase 3", style=discord.ButtonStyle.blurple)
    button_fase3.callback = lambda inter: fase_3(inter)

    view = View()
    view.add_item(button_assumir)
    view.add_item(button_painel_staff)
    view.add_item(button_fechar)
    view.add_item(button_recrutamento)
    view.add_item(button_fase2)
    view.add_item(button_fase3)

    await ticket_channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Ticket criado: {ticket_channel.mention}", ephemeral=True)

async def assumir_ticket(interaction, usuario_abriu, canal):
    if not await verificar_cargo(interaction):
        await interaction.response.send_message("Você não tem permissão para assumir este ticket.", ephemeral=True)
        return

    membro = interaction.user
    await canal.set_permissions(membro, read_messages=True, send_messages=True)
    await canal.set_permissions(usuario_abriu, read_messages=True, send_messages=True)
    await canal.send(f"{membro.mention} irá assumir o ticket.")

async def painel_staff(interaction):
    if not await verificar_cargo(interaction):
        await interaction.response.send_message("Você não tem permissão para acessar o painel de staff.", ephemeral=True)
        return

    embed = discord.Embed(title="Painel de Staff", 
                          description="Aqui estão algumas opções para gerir o ticket:",
                          color=discord.Color.blurple())
    embed.add_field(name="Comandos Disponíveis", value="1. /fechar\n2. /transferir\n3. /escalar\n4. /recrutamento", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def fechar_ticket(interaction, usuario_abriu, canal):

    await canal.send(f"O ticket foi fechado por {interaction.user.mention}.")

    # Enviar transcrição em privado para quem abriu o ticket
    transcricao = "Agradecemos pelo seu contacto, se a sua dúvida ainda não ficou esclarecida, não hesite em abrir outro ticket. Cumprimentos da Direção da PJ"
    try:
        await usuario_abriu.send(transcricao)
    except discord.Forbidden:
        await canal.send(f"{usuario_abriu.mention}, não consigo enviar-te uma mensagem privada.")

    # Deletar o canal do ticket
    await canal.delete()

async def Recrutamento(interaction, usuario):
    if not await verificar_cargo(interaction):
        await interaction.response.send_message("Você não tem permissão para acessar a fase de recrutamento.", ephemeral=True)
        return

    # Enviar mensagem de recrutamento no canal do ticket
    mensagem = (
        f"Olá {usuario.mention}, para fazeres parte da Polícia Judiciária tens de preencher este formulário (link em baixo). "
        "Depois de preencheres o formulário, mencionas-me e dizes que já acabaste. Assim que disseres isso, eu vou avaliar o teu formulário e esperar por uma resposta.\n\n"
        "Link do formulário: https://docs.google.com/forms/d/e/1FAIpQLScGJUvmuKvRsTfoqSac_eIdvxSXys6XWNv6trYtVPpWV4kRuQ/viewform?usp=sf_link\n"
        "Atenciosamente,\nA direção da PJ"
    )
    await interaction.response.send_message(mensagem)

    # Adiciona os botões para fases 2 e 3
    button_fase2 = Button(label="Fase 2", style=discord.ButtonStyle.blurple)
    button_fase2.callback = lambda inter: fase_2(inter, usuario)

    button_fase3 = Button(label="Fase 3", style=discord.ButtonStyle.red)
    button_fase3.callback = lambda inter: fase_3(inter)

    view = View()
    view.add_item(button_fase2)
    view.add_item(button_fase3)

    await interaction.followup.send(view=view)

async def fase_2(interaction, usuario):
    if not await verificar_cargo(interaction):
        await interaction.response.send_message("Você não tem permissão para acessar a fase 2.", ephemeral=True)
        return

    perguntas = (
        "Agora vais ter 15 minutos para ler o código de conduta da PJ e no final irás responder a 5 questões.\n"
        "Boa sorte.\n"         "https://docs.google.com/document/d/14OX4Cf60v0nLyC61F2Q3npePB-WrzhlsSlDQbeJImZA/edit?usp=sharing"
    )
    await interaction.response.send_message(perguntas)

async def fase_3(interaction):
    if not await verificar_cargo(interaction):
        await interaction.response.send_message("Você não tem permissão para acessar a fase 3.", ephemeral=True)
        return

    perguntas = (
        "1 - Em que situação podes patrulhar de mota?\n"
        "2 - Descreve como farias uma situação de fuga limpa.\n"
        "3 - Descreve pelo menos 1 direito do cidadão ao ser preso.\n"
        "4 - Num BMW com 4 pessoas, quem seria a pessoa que mandaria iniciar a abordagem?\n"
        "5 - Em caso de um fugitivo no P2 de um carro à frente com menos ou igual número que vocês, apontar arma para trás, o que devem fazer?"
    )
    await interaction.response.send_message(perguntas)

keep_alive()
bot.run("")  # Substitua pelo token do seu bot
