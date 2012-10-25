(function() {
    var $;
    if (typeof window.grp == 'object' && typeof grp.jQuery != 'undefined') {
        $ = grp.jQuery;
    } else if (typeof window.django == 'object' && typeof django.jQuery != 'undefined') {
        $ = django.jQuery;
    } else {
        $ = jQuery;
    }

    (function() {
        var prefixCache = {};

        $.fn.curationPrefix = function() {
            if (!this.length) {
                return;
            }
            var elementId = this.attr('id');
            if (typeof(elementId) != 'string' || elementId.indexOf('id_') !== 0) {
                return;
            }
            var $this = (this.length > 1) ? $(this[0]) : this;
            var elementData = $this.data();
            if (typeof elementData != 'object' || !elementData.fieldName) {
                return;
            }
            var cacheKey = elementData.fieldName + elementId;
            if (typeof prefixCache[cacheKey] != 'undefined') {
                return prefixCache[cacheKey];
            }
            var regex = elementData.regex;
            if (!regex) {
                regex = new RegExp("^(.+\\-\\d+\\-)" + elementData.fieldName + "$");
                $this.data('regex', regex);
            }
            var matches = elementId.match(regex);
            if (!matches) {
                return;
            }
            prefixCache[cacheKey] = matches[1];
            return prefixCache[cacheKey];
        };

        $.fn.curationCtField = function() {
            if (!this.length) {
                return;
            }
            var $this = (this.length > 1) ? $(this[0]) : this;
            var prefix = $this.curationPrefix();
            if (!prefix) { return; }

            var elementData = $this.data();
            if (!elementData.ctFieldName) {
                return;
            }
            return $('#' + prefix + elementData.ctFieldName);
        };

        $.fn.curationFkField = function() {
            if (!this.length) {
                return;
            }
            var $this = (this.length > 1) ? $(this[0]) : this;
            var prefix = $this.curationPrefix();
            if (!prefix) { return; }

            var elementData = $this.data();
            if (!elementData.fkFieldName) {
                return;
            }
            return $('#' + prefix + elementData.fkFieldName);
        };
    })();


    // Toggle the display:block/display:none styles of form rows and
    // inputs based on the currently selected option in `select` (a generic
    // content_type field)
    var toggleContentTypeFields = function($select) {
        var selectData = $select.data();

        var prefix = $select.curationPrefix();
        if (!prefix) {
            return;
        }

        var inlineRelatedId = prefix.replace(/^id_(.+)\-(\d+)\-$/, '$1$2');
        var $inlineRelated = $('#' + inlineRelatedId);

        $inlineRelated.find('input[placeholder],textarea[placeholder]').each(function(i, input) {
            input.removeAttribute('placeholder');
        });

        var selectValue = $select.val(),
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

        var $fkField = $select.curationFkField();

        // The data property `oldValue` on the generic content-type's
        // object_id field is a javascript object keyed on the select
        // field's value (i.e. the content_type_id), containing the
        // value of the object_id field at the time that the field
        // was changed.
        //
        // The purpose of maintaining this is that we reset the object_id
        // field's value = '' when the content_type select changes. This code
        // allows the user to change the content_type back and not lose the
        // original object_id that was entered.
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

        // If the content_type_id has changed to a value that was previously
        // selected and had an object_id associated with it, reset to that
        // object_id
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

    $.fn.curated_content_type = function() {
        var $this = (this.length > 1) ? $(this[0]) : this;
        var $fkField = $this.curationFkField();
        if (typeof($fkField) != 'object' || !$fkField.length) {
            return;
        }
        $fkField.addClass('curated-object-id');

        var fkFieldName = $this.data('fkFieldName');
        var rowSelector = '.' + fkFieldName + '.row' + ',' +
                          '.' + fkFieldName + '.grp-row';
        $fkField.closest(rowSelector).addClass('curated-object-id-row');

        toggleContentTypeFields($this);
        // Bind to the focus event to store the previous value
        $this.bind("focus", function(evt) {
            var $select = $(evt.target);
            var selectValue = $select.val();
            $select.data('previousValue', selectValue);
        });
        $this.bind("change", function(evt) {
            toggleContentTypeFields($(evt.target));
        });

        $this.curated_related_generic();
    };

    $(document).ready(function() {
        // Iterate through curated content_type select elements
        $('.curated-content-type-select').each(function(index, element) {
            $(element).curated_content_type();
        });
    });
})();