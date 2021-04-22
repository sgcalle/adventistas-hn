odoo.define('adm.application.condition', require => {

    require('web.core');

    let counter = 0;

    function toggleCoditionSelect(event) {
			const $otherToggleCheckbox = $(event.currentTarget);
			const $selectHealth = $otherToggleCheckbox.closest('div.row').find('select.js_select_health');
			const $inputHealth = $otherToggleCheckbox.closest('div.row').find('input.js_select_health');

			const isChecked = $otherToggleCheckbox.is(':checked');

			$selectHealth.toggle(!isChecked);
			$selectHealth.prop('disabled', isChecked);

			$inputHealth.toggle(isChecked);
			$inputHealth.prop('disabled', !isChecked);
	}

    function toggleAllergySelect(event) {
			const $otherToggleCheckbox = $(event.currentTarget);
			const $selectHealth = $otherToggleCheckbox.closest('div.row').find('select.js_allergy_select');
			const $inputHealth = $otherToggleCheckbox.closest('div.row').find('input.js_allergy_text');

			const isChecked = $otherToggleCheckbox.is(':checked');

			$selectHealth.toggle(!isChecked);
			$selectHealth.prop('disabled', isChecked);

			$inputHealth.toggle(isChecked);
			$inputHealth.prop('disabled', !isChecked);
        console.log("DSSADSADSDSAd")
	}

    function toggleMedicationSelect(event) {
			const $otherToggleCheckbox = $(event.currentTarget);
			const $selectHealth = $otherToggleCheckbox.closest('div.row').find('select.js_medication_select');
			const $inputHealth = $otherToggleCheckbox.closest('div.row').find('input.js_medication_text');

			const isChecked = $otherToggleCheckbox.is(':checked');

			$selectHealth.toggle(!isChecked);
			$selectHealth.prop('disabled', isChecked);

			$inputHealth.toggle(isChecked);
			$inputHealth.prop('disabled', !isChecked);
	}



    function removeNewCondition(event) {
        $(event.currentTarget).closest('[data-adm-rel]').remove();
    }

    
    function appendNewAllergy(event) {
        counter--;
        const $clonedNewConditionTemplate = $(document.getElementById('template_allergy')).clone();
        // We remove the style display none
        $clonedNewConditionTemplate.removeAttr( 'style');
        $clonedNewConditionTemplate.find('.js_allergy_toggle').on('change', toggleAllergySelect);
        $clonedNewConditionTemplate.find('input.js_allergy_text').hide().prop('disabled', true);

        const conditionList = document.getElementById('allergy_list');
        const newMany2manyRev = document.createElement('DIV');
        newMany2manyRev.dataset.admRel = "rel";
        $clonedNewConditionTemplate.appendTo(newMany2manyRev);
        $clonedNewConditionTemplate.find('.remove-rel-medical').on('click', removeNewCondition);
        // newMany2manyRev.appendChild(clonedNewConditionTemplate)
        conditionList.appendChild(newMany2manyRev);
    }
    
    function appendNewMedication(event) {
        counter--;
        const $clonedNewConditionTemplate = $(document.getElementById('template_medication')).clone();
        // We remove the style display none
        $clonedNewConditionTemplate.removeAttr('style');

        $clonedNewConditionTemplate.find('.js_medication_toggle').on('change', toggleMedicationSelect);
        $clonedNewConditionTemplate.find('input.js_medication_text').hide().prop('disabled', true);

        const conditionList = document.getElementById('medication_list');
        const newMany2manyRev = document.createElement('DIV');
        newMany2manyRev.dataset.admRel = "rel";
        $clonedNewConditionTemplate.appendTo(newMany2manyRev);
        $clonedNewConditionTemplate.find('.remove-rel-medical').on('click', removeNewCondition);
        // newMany2manyRev.appendChild(clonedNewConditionTemplate)
        conditionList.appendChild(newMany2manyRev);
    }
    
    function appendNewCondition(event) {
        counter--;
        const $clonedNewConditionTemplate = $(document.getElementById('template_condition')).clone();
        // We remove the style display none
        $clonedNewConditionTemplate.removeAttr('style');

        $clonedNewConditionTemplate.find('.js_condition_select').on('change', toggleCoditionSelect);
        $clonedNewConditionTemplate.find('input.js_select_health').hide().prop('disabled', true);
        const conditionList = document.getElementById('condition_list');
        const newMany2manyRev = document.createElement('DIV');
        newMany2manyRev.dataset.admRel = "rel";
        $clonedNewConditionTemplate.appendTo(newMany2manyRev);
        $clonedNewConditionTemplate.find('.remove-rel-medical').on('click', removeNewCondition);
        // newMany2manyRev.appendChild(clonedNewConditionTemplate)
        conditionList.appendChild(newMany2manyRev);
    }

    $(document).ready(event => {
        $('.add-condition').on('click', appendNewCondition);
        $('.remove-rel-medical').on('click', removeNewCondition);

        $('.js_condition_select').on('change', toggleCoditionSelect);
        $('.js_allergy_toggle').on('change', toggleAllergySelect);
        $('.js_medication_toggle').on('change', toggleMedicationSelect);

        $('button.add-medical_condition').on('click', appendNewCondition);
        $('button.add-medical_allergy').on('click', appendNewAllergy);
        $('button.add-medical_medication').on('click', appendNewMedication);
    });

});