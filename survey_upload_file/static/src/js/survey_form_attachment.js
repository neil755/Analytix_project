/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import SurveyFormWidget from '@survey/js/survey_form';
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.SurveyFormUpload = publicWidget.Widget.extend({
    selector: '.o_survey_form',
    events: {
        'change .o_survey_upload_file': '_onFileChange',
        'click .o_survey_delete_files': '_onDeleteFiles'
    },

    init: function() {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },

    _onFileChange: function(ev) {
        const input = ev.target;
        const questionId = input.name;
        const multiple = input.hasAttribute('multiple');
        const files = Array.from(input.files);

        if (files.length === 0) return;

        // Validate file sizes (max 10MB per file)
        const maxSize = 10 * 1024 * 1024; // 10MB
        const invalidFiles = files.filter(file => file.size > maxSize);

        if (invalidFiles.length > 0) {
            alert(_t("Some files exceed the 10MB limit and won't be uploaded."));
            input.value = '';
            return;
        }

        this._readFiles(files).then((results) => {
            const validFiles = results.filter(r => r.success);
            const fileData = validFiles.map(r => r.data);
            const fileNames = validFiles.map(r => r.name);

            if (validFiles.length > 0) {
                $(input)
                    .attr('data-oe-data', JSON.stringify(fileData))
                    .attr('data-oe-file_name', JSON.stringify(fileNames));

                this._updateFileListDisplay(fileNames);
            } else {
                this._onDeleteFiles(ev);
            }
        });
    },

    _readFiles: function(files) {
        return Promise.all(files.map(file => {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = () => {
                    const data = reader.result.split(',')[1]; // Get base64 part
                    resolve({
                        success: true,
                        name: file.name,
                        data: data,
                        size: file.size
                    });
                };
                reader.onerror = () => {
                    resolve({ success: false });
                };
                reader.readAsDataURL(file);
            });
        }));
    },

    _updateFileListDisplay: function(fileNames) {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';

        if (fileNames.length === 0) {
            fileList.classList.add('d-none');
            return;
        }

        fileList.classList.remove('d-none');
        const ul = document.createElement('ul');
        ul.className = 'list-unstyled mb-2';

        fileNames.forEach((fileName) => {
            const li = document.createElement('li');
            li.className = 'd-flex align-items-center mb-1';

            li.innerHTML = `
                <i class="fa fa-paperclip mr-2"></i>
                <span class="text-truncate" style="max-width: 200px">${fileName}</span>
            `;
            ul.appendChild(li);
        });

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-link btn-sm o_survey_delete_files text-danger';
        deleteBtn.textContent = _t('Remove All');

        fileList.appendChild(ul);
        fileList.appendChild(deleteBtn);
    },

    _onDeleteFiles: function(ev) {
        ev.preventDefault();
        const input = $(ev.target).closest('.o_survey_upload_container').find('input[type="file"]')[0];

        $(input)
            .attr('data-oe-data', '')
            .attr('data-oe-file_name', '')
            .val('');

        document.getElementById('fileList').innerHTML = '';
        document.getElementById('fileList').classList.add('d-none');
    }
});
export default publicWidget.registry.SurveyFormUpload;