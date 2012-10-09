(function() {
    var $;
    if (typeof window.grp == 'object' && typeof grp.jQuery != 'undefined') {
        $ = grp.jQuery;
    } else if (typeof window.django == 'object' && typeof django.jQuery != 'undefined') {
        $ = django.jQuery;
    } else {
        $ = jQuery;
    }

    // Toggle the display:block/display:none styles of form rows and
    // inputs based on the currently selected option in `select` (a generic
    // content_type field)
    var toggleContentTypeFields = function(select) {
        var selectId = select.id;

        if (!selectId) {
            return;
        }

        var $select = $(select);
        var selectData = $select.data();

        var matches = selectId.match(selectData.regex);

        if (!matches) {
            return;
        }

        var prefix = matches[1];

        var $select = $(select),
            selectValue = $select.val(),
            previousSelectValue = $select.data('previousValue');

        // Whether one of the options which points to another field on this
        // model is the selected one. Is set inside the each() function below
        var ptrFieldSelected = false;

        $select.find('.curated-content-type-ptr').each(function(i, option) {
            var $option = $(option);
            var optionFieldName = $option.data('fieldName');
            var $optionField = $('#' + prefix + optionFieldName);
            if (!$optionField.length) {
                return;
            }
            if ($option.attr('value') == selectValue) {
                ptrFieldSelected = true;
                $optionField.show();
                $optionField.closest('.' + optionFieldName).show();
            } else {
                $optionField.hide();
                $optionField.closest('.' + optionFieldName).hide();
            }
        });

        var $fkField = $('#' + prefix + selectData.fkFieldName);

        // The data property `oldValue` on the generic content-type's
        // object_id field is a javascript object keyed on the select
        // field's value (i.e. the content_type_id), containing the
        // value of the object_id field at the time that the field
        // was changed.
        //
        // The purpose of maintaining this is that grappelli sets the
        // object_id field's value = '' when the content_type select changes.
        // This allows the user to seamlessly change the content_type back
        // with the old object_id intact.
        var oldValueData = $fkField.data('oldValue');
        if (!oldValueData) {
            oldValueData = {};
        }
        if (!previousSelectValue) {
            oldValueData[selectValue] = $fkField.val();
        } else {
            oldValueData[previousSelectValue] = $fkField.val();
        }
        $fkField.data('oldValue', oldValueData);

        if (ptrFieldSelected) {
            $fkField.hide();
            $fkField.closest('.' + selectData.fkFieldName).hide();
        } else {
            $fkField.show();
            $fkField.closest('.' + selectData.fkFieldName).show();
        }

        // Grappelli will reset the field to an empty string; if the
        // content_type_id has changed to a value that was previously selected
        // and had an object_id associated with it, reset to that object_id
        setTimeout(function() {
            var selectValue = $select.val();
            $select.data('previousValue', selectValue);
            if (ptrFieldSelected) { return; }

            var oldValueData = $fkField.data('oldValue');
            if (typeof oldValueData != 'object' || !oldValueData[selectValue]) {
                return;
            }
            var oldValue = oldValueData[selectValue];
            if ($fkField.val() === '' && typeof(oldValue) != 'undefined') {
                $fkField.val(oldValue);
                // Trigger change handlers so that the title is fetched for
                // the associated content object
                $fkField.trigger('change');
            }
        }, 12);
    };

    $(document).ready(function() {
        // Iterate through curated content_type select elements
        $('.curated-content-type-select').filter(function(index, element) {
            var $element = $(element);
            var fieldName = $element.data('fieldName');
            var elementId = $element.attr('id');
            if (!fieldName || !elementId) {
                return false;
            }
            var regex = new RegExp("^(.+\\-\\d+\\-)" + fieldName + "$");
            var matches = elementId.match(regex);
            // Filter out any elements which don't end match
            // /-\d+-{{content_type_field_name}}$/ (e.g. fields whose names
            // contain the strings '-empty' or '__prefix__')
            if (!matches) {
                return false;
            }
            var prefix = matches[1];
            var fkFieldName = $element.data('fkFieldName');
            var $fkField = $('#' + prefix + fkFieldName);
            $fkField.addClass('curated-object-id');

            var rowSelector = '.' + fkFieldName + '.row' + ',' +
                              '.' + fkFieldName + '.grp-row';
            $fkField.closest(rowSelector).addClass('curated-object-id-row');

            $element.data('regex', regex);

            toggleContentTypeFields(element);
            // Bind to the focus event to store the previous value
            $element.bind("focus", function(evt) {
                var $select = $(evt.target);
                var selectValue = $select.val();
                $select.data('previousValue', selectValue);
            });
            $element.bind("change", function(evt) {
                toggleContentTypeFields(evt.target);
            });
        });
    });
})();