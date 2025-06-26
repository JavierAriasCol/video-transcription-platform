// Configuración de la API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Referencias a elementos del DOM
const elements = {
    languageSelect: document.getElementById('language'),
    outputLanguageSelect: document.getElementById('outputLanguage'),
    uploadArea: document.getElementById('uploadArea'),
    videoFile: document.getElementById('videoFile'),
    fileInfo: document.getElementById('fileInfo'),
    fileName: document.getElementById('fileName'),
    fileSize: document.getElementById('fileSize'),
    fileDuration: document.getElementById('fileDuration'),
    removeFile: document.getElementById('removeFile'),
    transcribeBtn: document.getElementById('transcribeBtn'),
    progressSection: document.getElementById('progressSection'),
    resultsSection: document.getElementById('resultsSection'),
    errorSection: document.getElementById('errorSection'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    resultDuration: document.getElementById('resultDuration'),
    resultInputLanguage: document.getElementById('resultInputLanguage'),
    resultOutputLanguage: document.getElementById('resultOutputLanguage'),
    resultSegments: document.getElementById('resultSegments'),
    outputLanguageInfo: document.getElementById('outputLanguageInfo'),
    translationInfo: document.getElementById('translationInfo'),
    downloadBtn: document.getElementById('downloadBtn'),
    newTranscriptionBtn: document.getElementById('newTranscriptionBtn'),
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn')
};

// Variables globales
let selectedFile = null;
let downloadUrl = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkAPIConnection();
});

function initializeEventListeners() {
    // Eventos del selector de idioma
    elements.languageSelect.addEventListener('change', updateTranscribeButton);
    elements.outputLanguageSelect.addEventListener('change', updateTranscribeButton);

    // Eventos del área de upload
    elements.uploadArea.addEventListener('click', () => elements.videoFile.click());
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);

    // Evento del input de archivo
    elements.videoFile.addEventListener('change', handleFileSelect);

    // Evento para remover archivo
    elements.removeFile.addEventListener('click', removeSelectedFile);

    // Evento del botón de transcripción
    elements.transcribeBtn.addEventListener('click', startTranscription);

    // Eventos de los botones de resultado
    elements.downloadBtn.addEventListener('click', downloadVTTFile);
    elements.newTranscriptionBtn.addEventListener('click', resetApplication);
    elements.retryBtn.addEventListener('click', resetToUpload);
}

async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (!response.ok) {
            throw new Error('API no disponible');
        }
        console.log('✅ Conexión con API establecida');
    } catch (error) {
        console.error('❌ Error conectando con API:', error);
        showError('No se puede conectar con el servidor. Asegúrate de que el backend esté ejecutándose en http://127.0.0.1:8000');
    }
}

function handleDragOver(e) {
    e.preventDefault();
    elements.uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileSelection(file);
    }
}

async function handleFileSelection(file) {
    // Validar tipo de archivo
    if (!file.type.startsWith('video/')) {
        showError('Por favor selecciona un archivo de video válido.');
        return;
    }

    // Validar tamaño (máximo 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
        showError('El archivo es demasiado grande. Máximo 100MB.');
        return;
    }

    selectedFile = file;
    
    // Mostrar información del archivo
    elements.fileName.textContent = file.name;
    elements.fileSize.textContent = formatFileSize(file.size);
    
    // Obtener duración del video
    try {
        const duration = await getVideoDuration(file);
        elements.fileDuration.textContent = formatDuration(duration);
        
        // Validar duración (máximo 5 minutos)
        if (duration > 300) {
            showError('El video debe durar menos de 5 minutos.');
            removeSelectedFile();
            return;
        }
    } catch (error) {
        elements.fileDuration.textContent = 'Duración no disponible';
    }

    // Mostrar información del archivo y ocultar área de upload
    elements.uploadArea.style.display = 'none';
    elements.fileInfo.style.display = 'flex';
    
    updateTranscribeButton();
}

function getVideoDuration(file) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.preload = 'metadata';
        
        video.onloadedmetadata = function() {
            window.URL.revokeObjectURL(video.src);
            resolve(video.duration);
        };
        
        video.onerror = function() {
            reject(new Error('No se pudo obtener la duración del video'));
        };
        
        video.src = URL.createObjectURL(file);
    });
}

function removeSelectedFile() {
    selectedFile = null;
    elements.videoFile.value = '';
    elements.uploadArea.style.display = 'block';
    elements.fileInfo.style.display = 'none';
    updateTranscribeButton();
}

function updateTranscribeButton() {
    const hasFile = selectedFile !== null;
    const hasLanguage = elements.languageSelect.value !== '';
    
    elements.transcribeBtn.disabled = !(hasFile && hasLanguage);
}

async function startTranscription() {
    if (!selectedFile || !elements.languageSelect.value) {
        showError('Por favor selecciona un archivo y un idioma.');
        return;
    }

    // Ocultar secciones anteriores y mostrar progreso
    hideAllSections();
    elements.progressSection.style.display = 'block';

    // Preparar FormData
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', elements.languageSelect.value);
    
    // Agregar idioma de salida si está seleccionado
    if (elements.outputLanguageSelect.value) {
        formData.append('output_language', elements.outputLanguageSelect.value);
    }

    const needsTranslation = elements.outputLanguageSelect.value &&
                           elements.outputLanguageSelect.value !== elements.languageSelect.value;

    try {
        // Simular progreso
        updateProgress(0, 'Iniciando transcripción...');
        updateStep(1, 'active');

        // Realizar petición
        const response = await fetch(`${API_BASE_URL}/transcribe`, {
            method: 'POST',
            body: formData
        });

        updateProgress(25, 'Subiendo archivo...');
        updateStep(1, 'completed');
        updateStep(2, 'active');

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en la transcripción');
        }

        updateProgress(50, 'Procesando video...');
        updateStep(2, 'completed');
        updateStep(3, 'active');

        const result = await response.json();

        if (needsTranslation) {
            updateProgress(65, 'Transcribiendo audio...');
            updateStep(3, 'completed');
            updateStep(4, 'active');
            
            updateProgress(85, 'Traduciendo texto...');
            updateStep(4, 'completed');
            updateStep(5, 'active');
            
            updateProgress(95, 'Generando archivo VTT...');
        } else {
            updateProgress(75, 'Generando archivo VTT...');
            updateStep(3, 'completed');
            updateStep(5, 'active');
        }

        // Simular tiempo de procesamiento final
        await new Promise(resolve => setTimeout(resolve, 1000));

        updateProgress(100, 'Transcripción completada');
        updateStep(5, 'completed');

        // Mostrar resultados
        showResults(result);

    } catch (error) {
        console.error('Error en transcripción:', error);
        showError(error.message || 'Error inesperado durante la transcripción');
    }
}

function updateProgress(percentage, text) {
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressText.textContent = text;
}

function updateStep(stepNumber, status) {
    const step = document.getElementById(`step${stepNumber}`);
    if (step) {
        step.className = `step ${status}`;
    }
}

function showResults(result) {
    hideAllSections();
    elements.resultsSection.style.display = 'block';

    // Mostrar información de resultados
    elements.resultDuration.textContent = `${result.duration} segundos`;
    elements.resultInputLanguage.textContent = getLanguageDisplay(result.input_language);
    elements.resultSegments.textContent = `${result.segments_count} segmentos`;

    // Mostrar información de traducción si aplica
    if (result.translated) {
        elements.outputLanguageInfo.style.display = 'flex';
        elements.translationInfo.style.display = 'flex';
        elements.resultOutputLanguage.textContent = getLanguageDisplay(result.output_language);
    } else {
        elements.outputLanguageInfo.style.display = 'none';
        elements.translationInfo.style.display = 'none';
    }

    // Guardar URL de descarga
    downloadUrl = `${API_BASE_URL}${result.download_url}`;
}

function showError(message) {
    hideAllSections();
    elements.errorSection.style.display = 'block';
    elements.errorMessage.textContent = message;
}

function hideAllSections() {
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
}

function downloadVTTFile() {
    if (downloadUrl) {
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `transcription_${Date.now()}.vtt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function resetApplication() {
    // Limpiar archivo seleccionado
    removeSelectedFile();
    
    // Resetear selectores de idioma
    elements.languageSelect.value = '';
    elements.outputLanguageSelect.value = '';
    
    // Ocultar todas las secciones
    hideAllSections();
    
    // Limpiar variables
    downloadUrl = null;
    
    // Resetear pasos de progreso
    for (let i = 1; i <= 5; i++) {
        updateStep(i, '');
    }
    
    // Resetear barra de progreso
    updateProgress(0, '');
}

function resetToUpload() {
    hideAllSections();
}

// Función para mostrar idiomas con banderas
function getLanguageDisplay(language) {
    const languageMap = {
        'auto': '🔍 Detectar automáticamente',
        'spanish': '🇪🇸 Español',
        'english': '🇺🇸 English',
        'french': '🇫🇷 Français',
        'german': '🇩🇪 Deutsch',
        'italian': '🇮🇹 Italiano',
        'portuguese': '🇵🇹 Português',
        'russian': '🇷🇺 Русский',
        'japanese': '🇯🇵 日本語',
        'korean': '🇰🇷 한국어',
        'chinese': '🇨🇳 中文'
    };
    
    return languageMap[language] || language;
}

// Funciones de utilidad
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Manejo de errores globales
window.addEventListener('error', function(e) {
    console.error('Error global:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Promise rechazada:', e.reason);
});