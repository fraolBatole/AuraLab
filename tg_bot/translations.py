from enum import Enum
from tg_bot.user_settings import Language

# Dictionary to store translations
# The keys are the original English strings (or unique keys)
# The values are dictionaries mapping Language enum to the translated string
translations = {
    "🖼 Create Image": {
        Language.ENGLISH: "🖼 Create Image",
        Language.AMHARIC: "🖼 ምስል ፍጠር",
    },
    "🎥 Create Video": {
        Language.ENGLISH: "🎥 Create Video",
        Language.AMHARIC: "🎥 ቪዲዮ ፍጠር",
    },
    "❓ Help": {
        Language.ENGLISH: "❓ Help",
        Language.AMHARIC: "❓ እገዛ",
    },
    "⚙️ Settings": {
        Language.ENGLISH: "⚙️ Settings",
        Language.AMHARIC: "⚙️ ቅንብሮች",
    },
    "➕ Top Up": {
        Language.ENGLISH: "➕ Top Up",
        Language.AMHARIC: "➕ መሙላት",
    },
    "💰 Balance": {
        Language.ENGLISH: "💰 Balance",
        Language.AMHARIC: "💰 ሒሳብ",
    },
    "⬅️ Back to Settings": {
        Language.ENGLISH: "⬅️ Back to Settings",
        Language.AMHARIC: "⬅️ ወደ ቅንብሮች ተመለስ",
    },
     "📐 Aspect Ratio": {
        Language.ENGLISH: "📐 Aspect Ratio",
        Language.AMHARIC: "📐 የምስል ምጥጥን",
    },
    "🌐 Language": {
        Language.ENGLISH: "🌐 Language",
        Language.AMHARIC: "🌐 ቋንቋ",
    },
    "welcome": {
        Language.ENGLISH: "Welcome to AuraLabs, {user_name}!",
        Language.AMHARIC: "እንኳን ወደ AuraLabs በደህና መጡ, {user_name}!",
    },
    "welcome_language_select": {
        Language.ENGLISH: (
            "🌟 Welcome to AuraLabs!\n\n"
            "✨ AI-powered creative studio at your fingertips\n\n"
            "Features:\n"
            "🖼️ Generate stunning images from text\n"
            "🎥 Create dynamic videos\n\n"
            "Please select your preferred language to get started:"
        ),
        Language.AMHARIC: (
            "🌟 እንኳን ወደ AuraLabs በደህና መጡ!\n\n"
            "✨ በAI የሚሰራ የስብጥነት ስቱዲዮ በእርስዎ እጅ ጫፍ ላይ\n\n"
            "ባህርያት:\n"
            "🖼️ ከጽሁፍ አስደናቂ ምስሎች ይፍጠሩ\n"
            "🎥 ተለዋዋጭ ቪዲዮዎች ይፍጠሩ\n\n"
            "እባክዎ ለመጀመር የሚመርጡትን ቋንቋ ይምረጡ:"
        ),
    },
    "choose_action": {
        Language.ENGLISH: "🚀 Quick prompt presets to try out our bot:",
        Language.AMHARIC: "🚀 የእኛን ቦት ለመሞከር ፈጣን የሆኑ ቅድመ-ቅምጦች:",
    },
    "help_message": {
        Language.ENGLISH: (
            "🤖 AuraLabs Bot Help\n\n"
            "🖼️ Create Image: Generate images from text prompts\n"
            "🎥 Create Video: Choose between text-only or image-based video generation\n"
            "⚙️ **Settings**: Configure aspect ratios and language preferences\n\n"
            "To use the bot, you'll need to top up your account. This feature is coming soon!\n\n"
            "For images: Just type a description and I'll create it!\n"
            "For videos: Choose your preferred method - pure text description or start with an image reference."
        ),
        Language.AMHARIC: (
            "🤖 የ AuraLabs Bot እገዛ\n\n"
            "🖼️ ምስል ፍጠር: ከጽሁፍ መግለጫዎች ምስሎችን ይፍጠሩ\n"
            "🎥 ቪዲዮ ፍጠር: ጽሁፍ ብቻ ወይም ከምስል ጋር የቪዲዮ መፍጠር አማራጮች ይምረጡ\n"
            "⚙️ ቅንብሮች: የምስል ምጥጥን እና የቋንቋ ምርጫዎችን ያዋቅሩ\n\n"
            "ቦቱን ለመጠቀም አካውንትዎን መሙላት ያስፈልግዎታል። ይህ በቅርቡ የሚመጣ ነው!\n\n"
            "ለምስሎች: ገለፃ ብቻ ይተይቡ እና እኔ እፈጥረዋለሁ!\n"
            "ለቪዲዮዎች: የሚፈልጉትን የመፍጠር ዘዴ ይምረጡ - ንፁህ ጽሁፍ መግለጫ ወይም ከምስል ማጣቀሻ ይጀምሩ።"
        ),
    },
    "settings_message": {
        Language.ENGLISH: "⚙️ Settings\n\nChoose what you want to configure:",
        Language.AMHARIC: "⚙️ ቅንብሮች\n\nምን ማዋቀር እንደሚፈልጉ ይምረጡ:",
    },
    "aspect_ratio_set_message": {
        Language.ENGLISH: "Aspect ratio set!",
        Language.AMHARIC: "የምስል ምጥጥን ተስተካክሏል!",
    },
    "aspect_ratio_set_confirmation": {
        Language.ENGLISH: "✅ Aspect ratio set to {ratio_value}\n\nYou can now generate images with this ratio.",
        Language.AMHARIC: "✅ የምስል ምጥጥን ወደ {ratio_value} ተቀናብሯል\n\nአሁን በዚህ ምጥጥን ምስሎችን መፍጠር ይችላሉ።",
    },
    "unknown_ratio_message": {
        Language.ENGLISH: "Unknown ratio",
        Language.AMHARIC: "ያልታወቀ ምጥጥን",
    },
    "language_set_message": {
        Language.ENGLISH: "Language set!",
        Language.AMHARIC: "ቋንቋ ተስተካክሏል!",
    },
    "language_set_confirmation": {
        Language.ENGLISH: "✅ Language set to {language_value}\n\nYour bot interface language has been updated.",
        Language.AMHARIC: "✅ ቋንቋ ወደ {language_value} ተቀናብሯል\n\nየእርስዎ ቦት በይነገጽ ቋንቋ ተዘምኗል።",
    },
    "unknown_language_message": {
        Language.ENGLISH: "Unknown language",
        Language.AMHARIC: "ያልታወቀ ቋንቋ",
    },
    "choose_aspect_ratio_message": {
        Language.ENGLISH: "Choose an aspect ratio:",
        Language.AMHARIC: "የምስል ምጥጥን ይምረጡ:",
    },
    "choose_language_message": {
        Language.ENGLISH: "Choose your language:",
        Language.AMHARIC: "ቋንቋዎን ይምረጡ:",
    },
    "settings_title": {
        Language.ENGLISH: "Settings:",
        Language.AMHARIC: "ቅንብሮች:",
    },
    "image_prompt_message": {
        Language.ENGLISH: "Describe the image you want to generate. If you want to change the aspect ratio, use the settings button:",
        Language.AMHARIC: "ሊፈጥሩት የሚፈልጉትን ምስል ይግለጹ። የምስል ምጥጥን መቀየር ከፈለጉ የቅንብሮች አዝራሩን ይጠቀሙ:",
    },
    "empty_description_message": {
        Language.ENGLISH: "Please provide a non-empty description.",
        Language.AMHARIC: "እባክዎ ባዶ ያልሆነ መግለጫ ያቅርቡ።",
    },
    "in_progress_message": {
        Language.ENGLISH: "in progress...",
        Language.AMHARIC: "በሂደት ላይ...",
    },
    "image_generation_failed_message": {
        Language.ENGLISH: "Failed to generate image.",
        Language.AMHARIC: "ምስል መፍጠር አልተሳካም።",
    },
    "image_generation_not_configured_message": {
        Language.ENGLISH: "Image generation is not configured.",
        Language.AMHARIC: "ምስል መፍጠር አልተዋቀረም።",
    },
    "video_generation_choice": {
        Language.ENGLISH: (
            "🎥 Video Generation\n\n"
            "Choose how you'd like to create your video:"
        ),
        Language.AMHARIC: (
            "🎥 ቪዲዮ መፍጠር\n\n"
            "ቪዲዮዎን እንዴት መፍጠር እንደሚፈልጉ ይምረጡ:"
        ),
    },
    "📝 Text Only": {
        Language.ENGLISH: "📝 Text Only",
        Language.AMHARIC: "📝 ከጽሁፍ ብቻ",
    },
    "🖼️ With Image": {
        Language.ENGLISH: "🖼️ From Image",
        Language.AMHARIC: "🖼️ ከምስል ወደ ቪዲዮ",
    },
    "video_text_only_prompt": {
        Language.ENGLISH: (
            "📝 Text-to-Video Generation\n\n"
            "Describe the video you want to create. Be as detailed as possible!\n\n"
            "For example:\n"
            "• 'Ethiopian male model walks confidently with a brown leather shoulder bag → Turns toward the camera → Offers a slight smile'\n"
            "• 'Coffee beans roll into frame → Bag slowly rotates to reveal label → Steam from a jebena forms your logo → Fade to call-to-action'\n"
            "• 'Hands grind beans close-up → Pour-over drips in slow motion → Latte art reveals slogan → CTA text slides in'\n\n"
            "What video would you like me to generate?"
        ),
        Language.AMHARIC: (
            "📝 ጽሁፍ-ወደ-ቪዲዮ መፍጠር\n\n"
            "ሊፈጥሩት የሚፈልጉትን ቪዲዮ ይግለጹ። በተቻለ መልክ ዝርዝር ያለ ይሁኑ!\n\n"
            "ለምሳሌ:\n"
            "• 'ኢትዮጵያዊ ወንድ ሞዴል በእምነት በቡናማ የቆዳ ጫነ ቦርሳ በሸክላ ላይ ይመላለሳል → ወደ ካሜራው ይዞራል → ትንሽ ሣቅ ይስጣል'\n"
            "• 'የቡና እህሎች ወደ ፎቶው ይግባሉ → ቦርሳው ምልክቱን ለማሳየት በቀስታ ይዞራል → ከጀበና የሚወጣ ጭማቂ ሎጎዎን ይገነባል → ወደ ኮል-ቶ-አክሽን በረድፍ ይጠፋ'\n"
            "• 'የእጆች ቅርብ እይታ ቡናን በሞርታር ይፍጫሉ → ፖር-ኦቨር በቀስታ ይወርዳል → የላቴ አርት ስሎጋንን ይገልጣል → የኮል-ቶ-አክሽን ጽሑፍ በቀስታ ይገባ'\n\n"
            "ምን አይነት ቪዲዮ እንድፈጥርልዎ ይፈልጋሉ?"
        ),
    },
    "video_generation_prompt": {
        Language.ENGLISH: (
            "🎥 Video Generation with Image\n\n"
            "To create a video, I need an image as reference. Please upload a photo that will inspire your video.\n\n"
            "After uploading the image, you'll be asked to describe what kind of video motion you want."
        ),
        Language.AMHARIC: (
            "🎥 ከምስል ጋር ቪዲዮ መፍጠር\n\n"
            "ቪዲዮ ለመፍጠር, እንደ ማጣቀሻ ምስል ያስፈልገኛል። እባክዎ ቪዲዮዎን የሚያነሳሳ ፎቶ ይስቀሉ።\n\n"
            "ምስሉን ከሰቀሉ በኋላ, ምን አይነት የቪዲዮ እንቅስቃሴ እንደሚፈልጉ እንዲገልጹ ይጠየቃሉ።"
        ),
    },
    "upload_photo_prompt": {
        Language.ENGLISH: "Please upload a photo. I need an image to use as reference for your video.",
        Language.AMHARIC: "እባክዎ ፎቶ ይስቀሉ። ለቪዲዮዎ እንደ ማጣቀሻ የምጠቀምበት ምስል ያስፈልገኛል።",
    },
    "processing_image_message": {
        Language.ENGLISH: "📸 Processing your image...",
        Language.AMHARIC: "📸 ምስልዎን በማዘጋጀት ላይ...",
    },
    "image_upload_success_prompt": {
        Language.ENGLISH: (
            "✅ Image uploaded successfully!\n\n"
            "Now describe the video you want to create. For example:\n"
            "• 'Make the scene come alive with gentle camera movement'\n"
            "• 'Create a dynamic pan showing the landscape'\n"
            "• 'Add motion to make it feel like a timelapse'\n\n"
            "What kind of video motion would you like?"
        ),
        Language.AMHARIC: (
            "✅ ምስል በተሳካ ሁኔታ ተሰቅሏል!\n\n"
            "አሁን ሊፈጥሩት የሚፈልጉትን ቪዲዮ ይግለጹ። ለምሳሌ:\n"
            "• 'በትእይንቱ ላይ በስሱ የካሜራ እንቅስቃሴ ህይወት ይዝሩበት'\n"
            "• 'የመሬት ገጽታውን የሚያሳይ ተለዋዋጭ ፓን ይፍጠሩ'\n"
            "• 'የጊዜ ማለፍ ስሜት እንዲሰማው እንቅስቃሴ ይጨምሩ'\n\n"
            "ምን አይነት የቪዲዮ እንቅስቃሴ ይፈልጋሉ?"
        ),
    },
    "image_processing_error_message": {
        Language.ENGLISH: "❌ Sorry, I couldn't process your image. Please try uploading it again.",
        Language.AMHARIC: "❌ ይቅርታ, ምስልዎን ማዘጋጀት አልቻልኩም። እባክዎ እንደገና ለመስቀል ይሞክሩ።",
    },
    "video_description_prompt": {
        Language.ENGLISH: "Please provide a description for your video.",
        Language.AMHARIC: "እባክዎ ለቪዲዮዎ መግለጫ ያቅርቡ።",
    },
    "uploaded_image_not_found_message": {
        Language.ENGLISH: "❌ I couldn't find your uploaded image. Please start the video generation process again.",
        Language.AMHARIC: "❌ የሰቀሉትን ምስል ማግኘት አልቻልኩም። እባክዎ የቪዲዮ መፍጠር ሂደቱን እንደገና ይጀምሩ።",
    },
    "video_generation_in_progress_message": {
        Language.ENGLISH: "🎬 Generating your video... This may take a few minutes.\nI'll notify you when it's ready!",
        Language.AMHARIC: "🎬 ቪዲዮዎን በመፍጠር ላይ... ይህ ጥቂት ደቂቃዎችን ሊወስድ ይችላል።\nዝግጁ ሲሆን አሳውቅዎታለሁ!",
    },
    "video_progress": {
        Language.ENGLISH: "⏳ Progress update: {progress}",
        Language.AMHARIC: "⏳ የሂደት ዝማኔ: {progress}",
    },
    "video_generation_not_configured_message": {
        Language.ENGLISH: "Video generation is not configured.",
        Language.AMHARIC: "ቪዲዮ መፍጠር አልተዋቀረም።",
    },
    "video_ready_caption": {
        Language.ENGLISH: "🎥 Your video is ready!\n\nPrompt: {prompt}",
        Language.AMHARIC: "🎥 ቪዲዮዎ ዝግጁ ነው!\n\nመግለጫ: {prompt}",
    },
    "video_generation_failed_message": {
        Language.ENGLISH: "❌ Sorry, I couldn't generate your video. Please try again with a different prompt or image.",
        Language.AMHARIC: "❌ ይቅርታ, ቪዲዮዎን መፍጠር አልቻልኩም። እባክዎ በተለየ መግለጫ ወይም ምስል እንደገና ይሞክሩ።",
    },
    "video_generation_error_message": {
        Language.ENGLISH: "❌ An error occurred while generating your video. Please try again.",
        Language.AMHARIC: "❌ ቪዲዮዎን በሚፈጥሩበት ጊዜ ስህተት ተከስቷል። እባክዎ እንደገና ይሞክሩ።",
    },
    "video_generation_timeout_message": {
        Language.ENGLISH: "⏰ Video generation is taking longer than expected. This sometimes happens with complex prompts. Please try again with a simpler description or try again later.",
        Language.AMHARIC: "⏰ ቪዲዮ መፍጠር ከሚለመደው በላይ ጊዜ እየወሰደ ነው። ይህ ብዙውን ጊዜ በተለያዩ መግለጫዎች ላይ ያስተካክላል። እባክዎ በተለየ መግለጫ እንደገና ይሞክሩ ወይም ቀጥሎ ይሞክሩ።",
    },
    "video_generation_quota_message": {
        Language.ENGLISH: "❌ You've reached your video generation quota. Please try again later or contact support for increased limits.",
        Language.AMHARIC: "❌ የቪዲዮ መፍጠር መጠን ለመጠናቀቅ ተሻለ። እባክዎ ቀጥሎ ይሞክሩ ወይም ለተሻለ መጠን ድጋፍ ያግኙ።",
    },
    "video_generation_cancelled_previous": {
        Language.ENGLISH: "🔄 Cancelled your previous video generation request to start a new one.",
        Language.AMHARIC: "🔄 አዲስ ቪዲዮ መፍጠር ለመጀመር ያለፈውን ቪዲዮ መፍጠር ጥያቄ ሰረዝክ።",
    },
    "image_generation_choice": {
        Language.ENGLISH: (
            "🖼️ Image Generation\n\n"
            "Choose how you'd like to create your image:"
        ),
        Language.AMHARIC: (
            "🖼️ ምስል መፍጠር\n\n"
            "ምስልዎን እንዴት መፍጠር እንደሚፈልጉ ይምረጡ:"
        ),
    },
    "image_to_image_upload_prompt": {
        Language.ENGLISH: (
            "🖼️ Image-to-Image Generation\n\n"
            "To create a new image based on an existing one, I need a reference image. Please upload a photo that will inspire your new creation.\n\n"
            "After uploading the image, you'll be asked to describe what changes or style you want for the new image."
        ),
        Language.AMHARIC: (
            "🖼️ ምስል-ወደ-ምስል መፍጠር\n\n"
            "አንድ አዲስ ምስል በነባር ምስል ላይ በመመስረት ለመፍጠር, እንደ ማጣቀሻ ምስል ያስፈልገኛል። እባክዎ አዲስ ፍጥረትዎን የሚያነሳሳ ፎቶ ይስቀሉ።\n\n"
            "ምስሉን ከሰቀሉ በኋላ, ለአዲሱ ምስል ምን አይነት ለውጦች ወይም ዘይቤ እንደሚፈልጉ እንዲገልጹ ይጠየቃሉ።"
        ),
    },
    "image_upload_success_prompt_for_image_gen": {
        Language.ENGLISH: (
            "✅ Image uploaded successfully!\n\n"
            "Now describe how you'd like to transform this image. For example:\n"
            "• 'Make me wear traditional Ethiopian clothing'\n"
            "• 'Place me at the center of a bustling Addis Ababa market'\n"
            "• 'Reimagine me as a character in a classic Hollywood film'\n"
            "• 'Transform the image into a vibrant Ethiopian coffee ceremony scene'\n"
            "• 'Make it look like a comic book superhero'\n\n"
            "How would you like me to transform your image?"
        ),
        Language.AMHARIC: (
            "✅ ምስል በተሳካ ሁኔታ ተሰቅሏል!\n\n"
            "አሁን ይህን ምስል እንዴት መቀየር እንደሚፈልጉ ይግለጹ። ለምሳሌ:\n"
            "• 'የኢትዮጵያ ባህላዊ ልብስ እንዲለብስ አድርገኝ'\n"
            "• 'በደመቀ የአዲስ አበባ ገበያ መሃል አስቀምጠኝ'\n"
            "• 'በአንድ ዝነኛ የሆሊውድ ፊልም ውስጥ ያለ ገጸ ባህሪ አድርገህ እንደገና ፍጠረኝ'\n"
            "• 'ምስሉን ወደ ኢትዮጵያ ቡና አፈላል ስነ-ስርዓት ቀይረው'\n"
            "• 'እንደ አስቂኝ መፅሃፍ ጀግና እንዲመስል አድርገው'\n\n"
            "ምስልዎን እንዴት ልለውጥልዎት ይፈልጋሉ?"
        ),
    },
    "📐 Image Aspect Ratio": {
        Language.ENGLISH: "📐 Image Aspect Ratio",
        Language.AMHARIC: "📐 የምስል ምጥጥን",
    },
    "🎞️ Video Aspect Ratio": {
        Language.ENGLISH: "🎞️ Video Aspect Ratio",
        Language.AMHARIC: "🎞️ የቪዲዮ ምጥጥን",
    },
    "choose_image_aspect_ratio_message": {
        Language.ENGLISH: "Choose an image aspect ratio:",
        Language.AMHARIC: "የምስል ምጥጥን ይምረጡ:",
    },
    "choose_video_aspect_ratio_message": {
        Language.ENGLISH: "Choose a video aspect ratio:",
        Language.AMHARIC: "የቪዲዮ ምጥጥን ይምረጡ:",
    },
    "video_ratio_set_message": {
        Language.ENGLISH: "Video aspect ratio set!",
        Language.AMHARIC: "የቪዲዮ ምጥጥን ተቀናበረ!",
    },
    "video_ratio_set_confirmation": {
        Language.ENGLISH: "✅ Video aspect ratio set to {ratio_value}\n\nYou can now generate videos with this ratio.",
        Language.AMHARIC: "✅ የቪዲዮ ምጥጥን ወደ {ratio_value} ተቀናበረ\n\nአሁን በዚህ ምጥጥን ቪዲዮዎችን መፍጠር ትችላለህ።",
    },
}

def get_translation(text_key: str, language: Language, **kwargs) -> str:
    """
    Retrieves the translated string for a given text key and language.
    Falls back to English if the translation is not available.
    Supports simple string formatting.
    """
    translation_template = translations.get(text_key, {}).get(language, text_key)
    return translation_template.format(**kwargs)

# ==========================
# Image Prompt Presets (i18n)
# ==========================

# Ordered list for stable keyboard pagination
PROMPT_PRESETS = [

    {
        "id": "ecommerce_fashion_models",
        "label": {
            Language.ENGLISH: "👗 Ethiopian Couture Brand Shoot",
            Language.AMHARIC: "👗 የኢትዮጵያ ቆንጆ ፋሽን ዘመቻ",
        },
        "prompt": {
            Language.ENGLISH: "Create a polished brand photoshoot of Ethiopian girl model wearing a Habesha Kemis with traditional patterns, ready for luxury fashion or cosmetics campaigns.",
            Language.AMHARIC: "በዘመናዊ ልብስ ውስጥ ባህላዊ ንድፎችን የጠመዱ ኢትዮጵያዊ ሞዴሎችን የሚያሳይ ተዋት ያለ የብራንድ ፎቶ ስቱዲዮ ፍጠር፣ ለውድ ፋሽን ወይም ለኮስሜቲክስ ዘመቻ ተስማሚ።",
        },
    },
    {
        "id": "timkat_festival",
        "label": {
            Language.ENGLISH: "🍺 Ethiopian Brewery Lifestyle Campaign",
            Language.AMHARIC: "🍺 የኢትዮጵያ ቢራ ዘመቻ",
        },
        "prompt": {
            Language.ENGLISH: "Design a vibrant advertising scene of Ethiopian friends enjoying premium beer with branded glassware inside a stylish lounge, perfect for brewery marketing materials.",
            Language.AMHARIC: "በዘመናዊ ላውንጅ ውስጥ በምርጥ የቢራ ብራንድ ብርጭቆ ላይ ኢትዮጵያዊ ጓደኞች እየደሰቱ የሚታዩ ንቁ የማስታወቂያ ትዕይንት አቀርብ፣ ለቢራ ፋብሪካዎች የገበያ ዕቃዎች ተገቢ።",
        },
    },
    {
        "id": "spice_postcard",
        "label": {
            Language.ENGLISH: "👜 Leather Heritage Brand Spotlight",
            Language.AMHARIC: "👜 የቆዳ ስራ ብራንድ ማብራት",
        },
        "prompt": {
            Language.ENGLISH: "Feature an Ethiopian girl model confidently holding handcrafted leather bags and accessories against a clean studio backdrop, tailored for premium leather goods catalogs and ads.",
            Language.AMHARIC: "በንጹህ የስቱዲዮ መድብ ፊት እጅ የተሠሩ የቆዳ ቦርሳዎችንና ንብረቶችን በእምነት የሚያሳይ ኢትዮጵያዊ ሞዴልን አቀርብ፣ ለውድ የቆዳ ምርቶች ካታሎግና ማስታወቂያ ተስማሚ።",
        },
    },
    {
        "id": "injera_family_restaurant",
        "label": {
            Language.ENGLISH: "🏢 Business Expo Cultural Showcase",
            Language.AMHARIC: "🏢 የንግድ ኤክስፖ ባህላዊ ትዕይንት",
        },
        "prompt": {
            Language.ENGLISH: "Portray Ethiopian entrepreneurs presenting branded products and services at a modern trade fair booth, integrating cultural motifs for corporate pitch decks and expo banners.",
            Language.AMHARIC: "የንግድ ትርፋማ ማቀናበሪያ ውስጥ ባህላዊ ንድፎችን ከዘመናዊ እቃዎቻቸው ጋር የሚያቀርቡ ኢትዮጵያዊ ኢንተርፕርነቶችን አቀርብ፣ ለኮርፖሬት የሽያጭ ትዕይንቶችና የኤክስፖ አስታዋቂዎች ተገቢ።",
        },
    },
]

# Translated UI strings for preset browsing
translations.update({
    "choose_preset_message": {
        Language.ENGLISH: "Choose a cultural/business image prompt:",
        Language.AMHARIC: "የባህላዊ/ንግድ ምስል መግለጫ ይምረጡ:",
    },
    "presets_prev": {
        Language.ENGLISH: "⬅️ Prev",
        Language.AMHARIC: "⬅️ ወደ ኋላ",
    },
    "presets_next": {
        Language.ENGLISH: "Next ➡️",
        Language.AMHARIC: "ወደ ፊት ➡️",
    },
    "image_generated_followup": {
        Language.ENGLISH: "Great image! Want to try video generation, custom prompts, or more cultural themes?",
        Language.AMHARIC: "ጥሩ ምስል! ቪዲዮ መፍጠር፣ ብጁ መግለጫዎች ወይም የባህል ጭብጥ ማሳያዎች ትፈልጋለህ?",
    },
    "retry_button": {
        Language.ENGLISH: "🔁 Retry",
        Language.AMHARIC: "🔁 እንደገና ሞክር",
    },
    "browse_presets_button": {
        Language.ENGLISH: "🔎 Browse Presets",
        Language.AMHARIC: "🔎 የቅድሚያ መግለጫዎች ይመልከቱ",
    },
    "coming_soon": {
        Language.ENGLISH: "Coming soon!",
        Language.AMHARIC: "በቅርቡ ይመጣል!",
    },
    "insufficient_image_credits": {
        Language.ENGLISH: "❌ You're out of image credits! You've used your promo credits. Please top up to continue generating images.",
        Language.AMHARIC: "❌ የምስል ክሬዲትህ አልቋል! የተለመድክ ክሬዲቶችን ተጠቅማህ። ምስል ለመፍጠር ክሬዲት ጨምር።",
    },
    "insufficient_video_credits": {
        Language.ENGLISH: "❌ You're out of video credits! Please top up to continue generating videos.",
        Language.AMHARIC: "❌ የቪዲዮ ክሬዲትህ አልቋል! ቪዲዮ ለመፍጠር ክሬዲት ጨምር።",
    },
    "image_credit_deducted": {
        Language.ENGLISH: "✅ Image generated! 1 credit deducted. Credits remaining: {remaining}",
        Language.AMHARIC: "✅ ምስል ተፈጠረ! 1 ክሬዲት ተራዘም። የቀሩ ክሬዲቶች: {remaining}",
    },
    "video_credit_deducted": {
        Language.ENGLISH: "✅ Video generated! 1 credit deducted. Credits remaining: {remaining}",
        Language.AMHARIC: "✅ ቪዲዮ ተፈጠረ! 1 ክሬዲት ተራዘም። የቀሩ ክሬዲቶች: {remaining}",
    },
    "balance_display": {
        Language.ENGLISH: "💰 Your Balance\n\n🖼️ Image Credits: {image_credits}\n🎥 Video Credits: {video_credits}\n\nGenerate amazing content with AuraLabs!",
        Language.AMHARIC: "💰 ሒሳብህ\n\n🖼️ የምስል ክሬዲቶች: {image_credits}\n🎥 የቪዲዮ ክሬዲቶች: {video_credits}\n\nከ AuraLabs ጋር እንቆቅልሽ ይዘቶችን ፍጠር!",
    },
})


def get_prompt_presets(language: Language):
    """Return list of dicts with id, label, prompt for the given language."""
    result = []
    for item in PROMPT_PRESETS:
        result.append({
            "id": item["id"],
            "label": item["label"].get(language, item["label"][Language.ENGLISH]),
            "prompt": item["prompt"].get(language, item["prompt"][Language.ENGLISH]),
        })
    return result


def get_prompt_by_id(prompt_id: str, language: Language) -> str | None:
    for item in PROMPT_PRESETS:
        if item["id"] == prompt_id:
            return item["prompt"].get(language, item["prompt"].get(Language.ENGLISH))
    return None
