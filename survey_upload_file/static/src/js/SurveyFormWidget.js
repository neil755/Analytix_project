/** @odoo-module */
import SurveyFormWidget from '@survey/js/survey_form';
SurveyFormWidget.include({
    _prepareSubmitValues: function(formData, params) {
        this._super.apply(this, arguments);

        this.$('[data-question-type="upload_file"]').each(function() {
            const $input = $(this);
            const data = $input.attr('data-oe-data');
            const fileNames = $input.attr('data-oe-file_name');

            if (data && fileNames && data !== '""' && fileNames !== '""') {
                try {
                    params[this.name] = [
                        JSON.parse(data),
                        JSON.parse(fileNames)
                    ];
                } catch (e) {
                    console.error('Error parsing file upload data:', e);
                    params[this.name] = null;
                }
            } else {
                params[this.name] = null;
            }
        });
    }
});