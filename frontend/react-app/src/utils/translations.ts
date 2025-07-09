export interface TranslationKeys {
  title: string;
  subtitle: string;
  chat_interface: string;
  chat_placeholder: string;
  voice_recorder: string;
  audio_message: string;
  upload_label: string;
  record_label: string;
  recording_unavailable: string;
  processing_audio: string;
  thinking: string;
  audio_processing: string;
  audio_error: string;
  system_status: string;
  stt_system: string;
  llm_system: string;
  language_label: string;
  safety_label: string;
  safety_value: string;
  clear_chat: string;
  about_section: string;
  about_text: string;
  initializing: string;
  language_selector: string;
  error_prefix: string;
  audio_error_prefix: string;
  upload_success: string;
  process_button: string;
  emergency_contacts: string;
  emergency_info: string;
  general_emergency: string;
  sultan_hospital: string;
  mental_health_hotline: string;
  emergency_desc: string;
  hospital_desc: string;
  hotline_desc: string;
  available_24_7: string;
  crisis_support: string;
  crisis_message: string;
  emergency_alert: string;
  welcome_message: string;
  start_conversation: string;
  thinking_response: string;
  recording: string;
  recording_complete: string;
  process_audio: string;
  processing: string;
  upload_audio: string;
  drag_drop_audio: string;
  supported_formats: string;
  uploaded_file: string;
  invalid_file_type: string;
  microphone_error: string;
  empty_file: string;
  file_too_large: string;
}

export const translations: Record<'arabic' | 'english', TranslationKeys> = {
  arabic: {
    title: "المستشار النفسي العماني",
    subtitle: "نظام الرعاية الصحية النفسية المتقدم",
    chat_interface: "واجهة المحادثة",
    chat_placeholder: "اكتب رسالتك هنا...",
    voice_recorder: "مسجل الصوت",
    audio_message: "رسالة صوتية",
    upload_label: "تحميل ملف صوتي",
    record_label: "اضغط للتسجيل",
    recording_unavailable: "التسجيل غير متاح حاليًا",
    processing_audio: "جاري معالجة الصوت...",
    thinking: "جاري التفكير...",
    audio_processing: "معالجة الرسالة الصوتية...",
    audio_error: "خطأ في معالجة الرسالة الصوتية",
    system_status: "حالة النظام",
    stt_system: "نظام التعرف على الكلام",
    llm_system: "نظام الذكاء الاصطناعي",
    language_label: "اللغة",
    safety_label: "الأمان",
    safety_value: "ملتزم بالقيم الإسلامية والثقافة العمانية",
    clear_chat: "مسح المحادثة",
    about_section: "حول النظام",
    about_text: "نظام متقدم للرعاية الصحية النفسية مصمم خصيصاً للمجتمع العماني",
    initializing: "جاري تهيئة النظام...",
    language_selector: "اختر اللغة",
    error_prefix: "خطأ:",
    audio_error_prefix: "خطأ في الصوت:",
    upload_success: "تم تحميل الملف بنجاح",
    process_button: "معالجة الرسالة الصوتية",
    emergency_contacts: "جهات الاتصال الطارئة",
    emergency_info: "في حالة الطوارئ:",
    general_emergency: "الطوارئ العامة",
    sultan_hospital: "مستشفى السلطان قابوس الجامعي",
    mental_health_hotline: "خط المساعدة النفسية",
    emergency_desc: "للمساعدة الطارئة الفورية",
    hospital_desc: "المستشفى الجامعي الرئيسي",
    hotline_desc: "دعم نفسي متخصص",
    available_24_7: "متاح على مدار الساعة",
    crisis_support: "دعم الأزمات",
    crisis_message: "في حالة الأزمة، يرجى التواصل فوراً. المساعدة متاحة دائماً.",
    emergency_alert: "في حالة الطوارئ، اتصل فوراً",
    welcome_message: "أهلاً وسهلاً بك في المستشار النفسي العماني",
    start_conversation: "ابدأ المحادثة بكتابة رسالة أو استخدام الصوت",
    thinking_response: "أفهم مشاعرك وأقدر ثقتك. دعني أساعدك في هذا الأمر.",
    recording: "جاري التسجيل",
    recording_complete: "تم التسجيل بنجاح",
    process_audio: "معالجة الصوت",
    processing: "جاري المعالجة...",
    upload_audio: "تحميل ملف صوتي",
    drag_drop_audio: "اسحب وأسقط الملف الصوتي هنا أو انقر للاختيار",
    supported_formats: "الصيغ المدعومة: MP3, WAV, OGG, M4A",
    uploaded_file: "الملف المرفوع:",
    invalid_file_type: "نوع الملف غير مدعوم",
    microphone_error: "خطأ في الوصول للميكروفون",
    empty_file: "الملف الصوتي فارغ",
    file_too_large: "حجم الملف كبير جداً. الحد الأقصى هو 10 ميجابايت",
  },
  english: {
    title: "Omani Mental Health Counselor",
    subtitle: "Advanced Mental Healthcare System",
    chat_interface: "Chat Interface",
    chat_placeholder: "Type your message here...",
    voice_recorder: "Voice Recorder",
    audio_message: "Audio Message",
    upload_label: "Upload Audio File",
    record_label: "Press to Record",
    recording_unavailable: "Recording currently unavailable",
    processing_audio: "Processing audio...",
    thinking: "Processing...",
    audio_processing: "Processing voice message...",
    audio_error: "Error processing audio message",
    system_status: "System Status",
    stt_system: "Speech Recognition System",
    llm_system: "AI Processing System",
    language_label: "Language",
    safety_label: "Safety",
    safety_value: "Compliant with Islamic values and Omani culture",
    clear_chat: "Clear Chat",
    about_section: "About System",
    about_text: "Advanced mental healthcare system designed specifically for Omani society",
    initializing: "Initializing system...",
    language_selector: "Select Language",
    error_prefix: "Error:",
    audio_error_prefix: "Audio Error:",
    upload_success: "File uploaded successfully",
    process_button: "Process Voice Message",
    emergency_contacts: "Emergency Contacts",
    emergency_info: "In case of emergency:",
    general_emergency: "General Emergency",
    sultan_hospital: "Sultan Qaboos University Hospital",
    mental_health_hotline: "Mental Health Hotline",
    emergency_desc: "For immediate emergency assistance",
    hospital_desc: "Main university hospital",
    hotline_desc: "Specialized mental health support",
    available_24_7: "Available 24/7",
    crisis_support: "Crisis Support",
    crisis_message: "If you are in crisis, please reach out immediately. Help is always available.",
    emergency_alert: "In emergency, call immediately",
    welcome_message: "Welcome to the Omani Mental Health Counselor",
    start_conversation: "Start a conversation by typing a message or using voice",
    thinking_response: "I understand your feelings and appreciate your trust. Let me help you with this matter.",
    recording: "Recording",
    recording_complete: "Recording completed successfully",
    process_audio: "Process Audio",
    processing: "Processing...",
    upload_audio: "Upload Audio File",
    drag_drop_audio: "Drag and drop audio file here or click to select",
    supported_formats: "Supported formats: MP3, WAV, OGG, M4A",
    uploaded_file: "Uploaded file:",
    invalid_file_type: "Unsupported file type",
    microphone_error: "Microphone access error",
    empty_file: "The audio file appears to be empty",
    file_too_large: "File too large. Maximum size is 10MB.",
  },
};
