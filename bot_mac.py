from telethon import TelegramClient, events
import re

API_ID = 1234567 # Substitua pelo seu
API_HASH = 'seu_api_hash_aqui' # Substitua pelo seu

client = TelegramClient('minha_sessao', API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)\.buscar (.*)'))
async def buscar_mac(event):
    termo = event.pattern_match.group(1).upper().replace('SERIAL:', '').strip()
    await event.delete()
    
    chat = await event.get_chat()
    resultados = []
    seriais_encontrados = set()

    msg_status = await client.send_message('me', f"⏳ Busca inteligente ativada para '{termo}'...")

    contador = 0
    try:
        async for msg in client.iter_messages(chat, limit=None):
            contador += 1
            
            if contador % 10000 == 0:
                data_msg = msg.date.strftime("%d/%m/%Y") if msg.date else "Desconhecida"
                await msg_status.edit(f"⏳ Lendo histórico...\n🔍 Mensagens: {contador}\n📅 Data do relatório: **{data_msg}**")

            # Verifica de forma simples se as letras existem no texto (igual ao código que funcionou)
            if msg.text and termo in msg.text.upper():
                
                # A MÁGICA AQUI: Procura o termo seguido de letras ou números.
                # O {4,} exige que tenha pelo menos 4 caracteres ALÉM do termo (ex: UB + NTBF0 = 6 no total).
                # O (?<![A-Z]) impede que ele pegue partes do meio de um nome como n[UBIA].
                padrao = rf'(?<![A-Z0-9])({termo}[A-Z0-9]{{4,}})'
                match_mac = re.search(padrao, msg.text.upper())
                
                if match_mac:
                    serial = match_mac.group(1)
                    
                    if serial not in seriais_encontrados:
                        seriais_encontrados.add(serial)
                        
                        chat_id = str(chat.id).replace('-100', '')
                        link = f"https://t.me/c/{chat_id}/{msg.id}"
                        
                        match_login = re.search(r'Login:\s*([^\n]+)', msg.text, re.IGNORECASE)
                        login = match_login.group(1).strip() if match_login else "Não especificado"
                        
                        data_formatada = msg.date.strftime("%d/%m/%Y") if msg.date else ""
                        
                        resultados.append(f"🔗 [Ir para a mensagem]({link}) *(Data: {data_formatada})*\n**Equipamento:** `{serial}` | **Login:** {login}")
                        
                        if len(resultados) >= 70:
                            break

        if resultados:
            resposta = f"📡 **Encontrados {len(resultados)} resultados válidos para '{termo}':**\n\n"
            resposta += "\n\n".join(resultados)
            await msg_status.edit(resposta)
        else:
            await msg_status.edit(f"❌ Nenhum equipamento iniciando com '{termo}' foi encontrado em {contador} mensagens verificadas.")
            
    except Exception as e:
        await msg_status.edit(f"⚠️ Erro: {str(e)}")

print("Bot Híbrido Iniciado! O filtro anti-nomes falsos está ativado.")
client.start()
client.run_until_disconnected()