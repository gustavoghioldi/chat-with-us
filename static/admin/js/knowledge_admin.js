/**
 * Script para manejar la interfaz del admin de Knowledge según la categoría
 */
(function($) {
    'use strict';

    function toggleFieldsBasedOnCategory() {
        var category = $('#id_category').val();
        var textFields = $('.field-text, .field-formatted_text_preview');
        var urlFields = $('.field-url');

        if (category === 'website') {
            // Para websites: mostrar solo URL, ocultar campos de texto
            textFields.hide();
            urlFields.show();
        } else if (category === 'plain_document') {
            // Para documentos: mostrar campos de texto, ocultar URL
            textFields.show();
            urlFields.hide();
        } else {
            // Por defecto mostrar todo
            textFields.show();
            urlFields.show();
        }
    }

    function addCategoryHelperText() {
        var categoryField = $('#id_category');
        if (categoryField.length) {
            // Agregar texto de ayuda después del select
            var helpText = $('<p class="help category-help"></p>');
            helpText.html(
                '<strong>💡 Información sobre categorías:</strong><br>' +
                '📄 <strong>plain_document:</strong> Para documentos de texto, archivos CSV/JSON que se convertirán a Markdown<br>' +
                '🌐 <strong>website:</strong> Para sitios web que requieren scraping (solo necesita URL)'
            );

            // Remover texto de ayuda anterior si existe
            categoryField.parent().find('.category-help').remove();
            categoryField.after(helpText);
        }
    }

    $(document).ready(function() {
        // Solo ejecutar en páginas de add/change de knowledge
        if ($('body').hasClass('model-knowledgemodel')) {
            addCategoryHelperText();
            toggleFieldsBasedOnCategory();

            // Escuchar cambios en el campo categoría
            $('#id_category').on('change', function() {
                toggleFieldsBasedOnCategory();
            });
        }

        // Agregar estilos para mejorar la presentación
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                .category-help {
                    background-color: #f0f8ff;
                    padding: 10px;
                    border-left: 4px solid #007cba;
                    margin-top: 5px;
                    border-radius: 4px;
                }

                .field-formatted_text_preview pre {
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 12px;
                    line-height: 1.4;
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    padding: 10px;
                }

                .field-file_upload_actions .button {
                    font-size: 11px;
                    padding: 4px 8px;
                }
            `)
            .appendTo('head');
    });
})(django.jQuery);
