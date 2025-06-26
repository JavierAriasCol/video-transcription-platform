// Configuración de la API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Referencias a elementos del DOM
const elements = {
    // Navigation tabs
    transcriptionTab: document.getElementById('transcriptionTab'),
    subtitlingTab: document.getElementById('subtitlingTab'),
    transcriptionContent: document.getElementById('transcriptionContent'),
    subtitlingContent: document.getElementById('subtitlingContent'),
    
    // Transcription elements
    languageSelect: document.getElementById('language'),
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
    resultLanguage: document.getElementById('resultLanguage'),
    resultSegments: document.getElementById('resultSegments'),
    downloadBtn: document.getElementById('downloadBtn'),
    newTranscriptionBtn: document.getElementById('newTranscriptionBtn'),
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn'),
    
    // Subtitling elements
    subtitleVideoUploadArea: document.getElementById('subtitleVideoUploadArea'),
    subtitleVideoFile: document.getElementById('subtitleVideoFile'),
    subtitleVideoInfo: document.getElementById('subtitleVideoInfo'),
    subtitleVideoName: document.getElementById('subtitleVideoName'),
    subtitleVideoSize: document.getElementById('subtitleVideoSize'),
    removeSubtitleVideo: document.getElementById('removeSubtitleVideo'),
    vttUploadArea: document.getElementById('vttUploadArea'),
    vttFile: document.getElementById('vttFile'),
    vttFileInfo: document.getElementById('vttFileInfo'),
    vttFileName: document.getElementById('vttFileName'),
    vttFileSize: document.getElementById('vttFileSize'),
    removeVttFile: document.getElementById('removeVttFile'),
    fontColor: document.getElementById('fontColor'),
    backgroundColor: document.getElementById('backgroundColor'),
    fontSize: document.getElementById('fontSize'),
    backgroundOpacity: document.getElementById('backgroundOpacity'),
    opacityValue: document.getElementById('opacityValue'),
    generateSubtitlesBtn: document.getElementById('generateSubtitlesBtn'),
    subtitlingProgressSection: document.getElementById('subtitlingProgressSection'),
    subtitlingResultsSection: document.getElementById('subtitlingResultsSection'),
    subtitlingErrorSection: document.getElementById('subtitlingErrorSection'),
    subtitlingProgressFill: document.getElementById('subtitlingProgressFill'),
    subtitlingProgressText: document.getElementById('subtitlingProgressText'),
    subtitlingResultDuration: document.getElementById('subtitlingResultDuration'),
    subtitlingResultSubtitles: document.getElementById('subtitlingResultSubtitles'),
    subtitlingResultSize: document.getElementById('subtitlingResultSize'),
    downloadSubtitledVideoBtn: document.getElementById('downloadSubtitledVideoBtn'),
    newSubtitlingBtn: document.getElementById('newSubtitlingBtn'),
    subtitlingErrorMessage: document.getElementById('subtitlingErrorMessage'),
    retrySubtitlingBtn: document.getElementById('retrySubtitlingBtn')
};

// Variables globales
let selectedFile = null;
let downloadUrl = null;
let selectedSubtitleVideo = null;
let selectedVttFile = null;
let subtitledVideoDownloadUrl = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkAPIConnection();
});

function initializeEventListeners() {
    // Navigation tabs
    elements.transcriptionTab.addEventListener('click', () => switchTab('transcription'));
    elements.subtitlingTab.addEventListener('click', () => switchTab('subtitling'));

    // Transcription events
    elements.languageSelect.addEventListener('change', updateTranscribeButton);
    elements.uploadArea.addEventListener('click', () => elements.videoFile.click());
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    elements.videoFile.addEventListener('change', handleFileSelect);
    elements.removeFile.addEventListener('click', removeSelectedFile);
    elements.transcribeBtn.addEventListener('click', startTranscription);
    elements.downloadBtn.addEventListener('click', downloadVTTFile);
    elements.newTranscriptionBtn.addEventListener('click', resetApplication);
    elements.retryBtn.addEventListener('click', resetToUpload);

    // Subtitling events
    elements.subtitleVideoUploadArea.addEventListener('click', () => elements.subtitleVideoFile.click());
    elements.subtitleVideoUploadArea.addEventListener('dragover', (e) => handleSubtitleDragOver(e, 'video'));
    elements.subtitleVideoUploadArea.addEventListener('dragleave', (e) => handleSubtitleDragLeave(e, 'video'));
    elements.subtitleVideoUploadArea.addEventListener('drop', (e) => handleSubtitleDrop(e, 'video'));
    elements.subtitleVideoFile.addEventListener('change', handleSubtitleVideoSelect);
    elements.removeSubtitleVideo.addEventListener('click', removeSubtitleVideo);
    
    elements.vttUploadArea.addEventListener('click', () => elements.vttFile.click());
    elements.vttUploadArea.addEventListener('dragover', (e) => handleSubtitleDragOver(e, 'vtt'));
    elements.vttUploadArea.addEventListener('dragleave', (e) => handleSubtitleDragLeave(e, 'vtt'));
    elements.vttUploadArea.addEventListener('drop', (e) => handleSubtitleDrop(e, 'vtt'));
    elements.vttFile.addEventListener('change', handleVttFileSelect);
    elements.removeVttFile.addEventListener('click', removeVttFile);
    
    elements.backgroundOpacity.addEventListener('input', updateOpacityValue);
    elements.generateSubtitlesBtn.addEventListener('click', startSubtitling);
    elements.downloadSubtitledVideoBtn.addEventListener('click', downloadSubtitledVideo);
    elements.newSubtitlingBtn.addEventListener('click', resetSubtitling);
    elements.retrySubtitlingBtn.addEventListener('click', resetSubtitlingToUpload);
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
        
        // Validar duración (máximo 2 minutos)
        if (duration > 120) {
            showError('El video debe durar menos de 2 minutos.');
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

        updateProgress(75, 'Generando archivo VTT...');
        updateStep(3, 'completed');
        updateStep(4, 'active');

        // Simular tiempo de procesamiento final
        await new Promise(resolve => setTimeout(resolve, 1000));

        updateProgress(100, 'Transcripción completada');
        updateStep(4, 'completed');

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
    elements.resultLanguage.textContent = getLanguageDisplay(result.language);
    elements.resultSegments.textContent = `${result.segments_count} segmentos`;

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
    
    // Resetear selector de idioma
    elements.languageSelect.value = '';
    
    // Ocultar todas las secciones
    hideAllSections();
    
    // Limpiar variables
    downloadUrl = null;
    
    // Resetear pasos de progreso
    for (let i = 1; i <= 4; i++) {
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
        'spanish': '🇪🇸 Español',
        'english': '🇺🇸 English'
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

// Tab switching functionality
function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    if (tab === 'transcription') {
        elements.transcriptionTab.classList.add('active');
        elements.transcriptionContent.classList.add('active');
    } else if (tab === 'subtitling') {
        elements.subtitlingTab.classList.add('active');
        elements.subtitlingContent.classList.add('active');
    }
}

// Subtitling drag and drop handlers
function handleSubtitleDragOver(e, type) {
    e.preventDefault();
    const area = type === 'video' ? elements.subtitleVideoUploadArea : elements.vttUploadArea;
    area.classList.add('dragover');
}

function handleSubtitleDragLeave(e, type) {
    e.preventDefault();
    const area = type === 'video' ? elements.subtitleVideoUploadArea : elements.vttUploadArea;
    area.classList.remove('dragover');
}

function handleSubtitleDrop(e, type) {
    e.preventDefault();
    const area = type === 'video' ? elements.subtitleVideoUploadArea : elements.vttUploadArea;
    area.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        if (type === 'video') {
            handleSubtitleVideoSelection(files[0]);
        } else {
            handleVttFileSelection(files[0]);
        }
    }
}

// Subtitle video file handling
function handleSubtitleVideoSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleSubtitleVideoSelection(file);
    }
}

function handleSubtitleVideoSelection(file) {
    // Validate video file
    if (!file.type.startsWith('video/')) {
        showSubtitlingError('Por favor selecciona un archivo de video válido.');
        return;
    }

    // Validate size (max 500MB for subtitling)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
        showSubtitlingError('El archivo es demasiado grande. Máximo 500MB.');
        return;
    }

    selectedSubtitleVideo = file;
    
    // Show file info
    elements.subtitleVideoName.textContent = file.name;
    elements.subtitleVideoSize.textContent = formatFileSize(file.size);
    
    // Hide upload area and show file info
    elements.subtitleVideoUploadArea.style.display = 'none';
    elements.subtitleVideoInfo.style.display = 'flex';
    
    updateGenerateButton();
}

function removeSubtitleVideo() {
    selectedSubtitleVideo = null;
    elements.subtitleVideoFile.value = '';
    elements.subtitleVideoUploadArea.style.display = 'block';
    elements.subtitleVideoInfo.style.display = 'none';
    updateGenerateButton();
}

// VTT file handling
function handleVttFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleVttFileSelection(file);
    }
}

function handleVttFileSelection(file) {
    // Validate VTT file
    if (!file.name.toLowerCase().endsWith('.vtt')) {
        showSubtitlingError('Por favor selecciona un archivo VTT válido.');
        return;
    }

    selectedVttFile = file;
    
    // Show file info
    elements.vttFileName.textContent = file.name;
    elements.vttFileSize.textContent = formatFileSize(file.size);
    
    // Hide upload area and show file info
    elements.vttUploadArea.style.display = 'none';
    elements.vttFileInfo.style.display = 'flex';
    
    updateGenerateButton();
}

function removeVttFile() {
    selectedVttFile = null;
    elements.vttFile.value = '';
    elements.vttUploadArea.style.display = 'block';
    elements.vttFileInfo.style.display = 'none';
    updateGenerateButton();
}

// Update opacity value display
function updateOpacityValue() {
    elements.opacityValue.textContent = elements.backgroundOpacity.value;
}

// Update generate button state
function updateGenerateButton() {
    const hasVideo = selectedSubtitleVideo !== null;
    const hasVtt = selectedVttFile !== null;
    
    elements.generateSubtitlesBtn.disabled = !(hasVideo && hasVtt);
}

// Start subtitling process
async function startSubtitling() {
    if (!selectedSubtitleVideo || !selectedVttFile) {
        showSubtitlingError('Por favor selecciona un video y un archivo VTT.');
        return;
    }

    // Hide sections and show progress
    hideAllSubtitlingSections();
    elements.subtitlingProgressSection.style.display = 'block';

    // Prepare FormData
    const formData = new FormData();
    formData.append('video', selectedSubtitleVideo);
    formData.append('vtt', selectedVttFile);
    formData.append('font_color', elements.fontColor.value);
    formData.append('background_color', elements.backgroundColor.value);
    formData.append('font_size', elements.fontSize.value);
    formData.append('background_opacity', elements.backgroundOpacity.value);

    try {
        // Update progress
        updateSubtitlingProgress(0, 'Iniciando proceso...');
        updateSubtitlingStep(1, 'active');

        // Make request
        const response = await fetch(`${API_BASE_URL}/subtitle`, {
            method: 'POST',
            body: formData
        });

        updateSubtitlingProgress(25, 'Subiendo archivos...');
        updateSubtitlingStep(1, 'completed');
        updateSubtitlingStep(2, 'active');

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en el subtitulado');
        }

        updateSubtitlingProgress(50, 'Procesando video...');
        updateSubtitlingStep(2, 'completed');
        updateSubtitlingStep(3, 'active');

        const result = await response.json();

        updateSubtitlingProgress(75, 'Añadiendo subtítulos...');
        updateSubtitlingStep(3, 'completed');
        updateSubtitlingStep(4, 'active');

        // Simulate final processing time
        await new Promise(resolve => setTimeout(resolve, 2000));

        updateSubtitlingProgress(100, 'Video subtitulado completado');
        updateSubtitlingStep(4, 'completed');

        // Show results
        showSubtitlingResults(result);

    } catch (error) {
        console.error('Error en subtitulado:', error);
        showSubtitlingError(error.message || 'Error inesperado durante el subtitulado');
    }
}

// Subtitling progress functions
function updateSubtitlingProgress(percentage, text) {
    elements.subtitlingProgressFill.style.width = `${percentage}%`;
    elements.subtitlingProgressText.textContent = text;
}

function updateSubtitlingStep(stepNumber, status) {
    const step = document.getElementById(`subStep${stepNumber}`);
    if (step) {
        step.className = `step ${status}`;
    }
}

function showSubtitlingResults(result) {
    hideAllSubtitlingSections();
    elements.subtitlingResultsSection.style.display = 'block';

    // Show result information
    elements.subtitlingResultDuration.textContent = `${result.duration} segundos`;
    elements.subtitlingResultSubtitles.textContent = `${result.subtitle_count} subtítulos`;
    elements.subtitlingResultSize.textContent = formatFileSize(result.file_size);

    // Save download URL
    subtitledVideoDownloadUrl = `${API_BASE_URL}${result.download_url}`;
}

function showSubtitlingError(message) {
    hideAllSubtitlingSections();
    elements.subtitlingErrorSection.style.display = 'block';
    elements.subtitlingErrorMessage.textContent = message;
}

function hideAllSubtitlingSections() {
    elements.subtitlingProgressSection.style.display = 'none';
    elements.subtitlingResultsSection.style.display = 'none';
    elements.subtitlingErrorSection.style.display = 'none';
}

function downloadSubtitledVideo() {
    if (subtitledVideoDownloadUrl) {
        const link = document.createElement('a');
        link.href = subtitledVideoDownloadUrl;
        link.download = `subtitled_video_${Date.now()}.mp4`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function resetSubtitling() {
    // Clear selected files
    removeSubtitleVideo();
    removeVttFile();
    
    // Reset options to defaults
    elements.fontColor.value = '#ffffff';
    elements.backgroundColor.value = '#000000';
    elements.fontSize.value = '20';
    elements.backgroundOpacity.value = '0.8';
    updateOpacityValue();
    
    // Hide all sections
    hideAllSubtitlingSections();
    
    // Clear variables
    subtitledVideoDownloadUrl = null;
    
    // Reset progress steps
    for (let i = 1; i <= 4; i++) {
        updateSubtitlingStep(i, '');
    }
    
    // Reset progress bar
    updateSubtitlingProgress(0, '');
}

function resetSubtitlingToUpload() {
    hideAllSubtitlingSections();
}