import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# processor.py file se hamara logic import ho raha hai
from processor import enhance_photo_with_depth 

# Log setup console par track rakhne ke liye
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- APNA TELEGRAM BOT TOKEN YAHAN PASTE KAREIN ---
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome! Main ek AI Depth Portrait Bot hun.\n\n"
        "📸 Mujhe koi bhi normal ya thodi blur photo bhejiye. "
        "Main uski Depth analyze karke, edges protect karke, aur professional "
        "Grain Matching apply karke use ekdum Real DSLR HD portrait bana dunga!"
    )
    await update.message.reply_text(welcome_text)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Photo mil gayi hai! AI Depth processing aur smart bokeh blending shuru ho rahi hai... Kripya thoda intezar karein.")
    
    # Photo files ka path setup
    input_path = "temp_input.jpg"
    output_path = "temp_output.jpg"
    
    try:
        # Telegram server se high resolution image download karna
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(input_path)
        
        # Processor engine chalana (Yeh hamari processor.py file se execute hoga)
        enhance_photo_with_depth(input_path, output_path)
        
        # Processed image wapas send karna
        await update.message.reply_photo(
            photo=open(output_path, 'rb'), 
            caption="✨ Ye lijiye! Depth-dependent blur aur digital grains ke saath aapki realistic HD photo taiyar hai."
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Processing ke dauran dikkat aayi: {str(e)}")
        
    finally:
        # Junk temporary files ko automatic clear karna space bachane ke liye
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

def main():
    # Application setup
    app = Application.builder().token(TOKEN).build()
    
    # Handlers assign karna
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    print("🚀 Telegram Depth Bot Successfully Run Ho Raha Hai...")
    app.run_polling()

if __name__ == '__main__':
    main()
  
