from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel
import yaml
import sys
import logging

# texto a reemplezar
find = '@example_1'
# texto que sustituye el anterior
replace = '@lucas 1'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    client = TelegramClient(config["session_name"], 
                            config["api_id"], 
                            config["api_hash"])
    client.start()

    input_channels_entities = []
    output_channel_entities = []
    for d in client.iter_dialogs():
        if d.name in config["input_channel_names"] or d.entity.id in config["input_channel_ids"]:
            input_channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
        if d.name in config["output_channel_names"] or d.entity.id in config["output_channel_ids"]:
            output_channel_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
            
    if not output_channel_entities:
        logger.error(f"No se pudo encontrar ningún canal de salida en los diálogos del usuario")
        sys.exit(1)

    if not input_channels_entities:
        logger.error(f"No se pudo encontrar ningún canal de entrada en los diálogos del usuario")
        sys.exit(1)
        
    logging.info(f"Leyendo en {len(input_channels_entities)} canales. Reenviando a {len(output_channel_entities)} canales.")
    
    @client.on(events.NewMessage(chats=input_channels_entities))
    async def handler(event):
        msg = event.message
        msg.replace(find, replace) # python hace todo el trabajo con replace()
        for output_channel in output_channel_entities:
            await client.forward_messages(output_channel, msg)

    client.run_until_disconnected()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} {{CONFIG_PATH}}")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        config = yaml.safe_load(f)
    start(config)
