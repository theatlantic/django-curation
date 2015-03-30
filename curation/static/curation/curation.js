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
                regex = new RegExp("^(id_|.+\\-(?:\\d+\\-)?)" + elementData.fieldName + "$");
                $this.data('regex', regex);
            }
            var matches = elementId.match(regex);
            if (!matches) {
                return;
            }
            prefixCache[cacheKey] = matches[1];
            return prefixCache[cacheKey];
        };

        $.fn.curationField = function(fieldName) {
            if (!this.length || !fieldName) {
                return;
            }
            var $this = (this.length > 1) ? $(this[0]) : this;
            var prefix = $this.curationPrefix();
            if (!prefix) { return; }

            return $('#' + prefix + fieldName);
        };

        $.fn.curationCtField = function() {
            if (!this.length) {
                return;
            }
            var $this = (this.length > 1) ? $(this[0]) : this,
                fieldName = $this.data('ctFieldName'),
                $ctField = $this.curationField(fieldName);

            if ($ctField && $ctField.length) {
                $ctField.data('fieldName', fieldName);
                var fkFieldName = $this.data('fkFieldName');
                if (fkFieldName) {
                    $ctField.data('fkFieldName', fkFieldName);
                }
                return $ctField;
            }
        };

        $.fn.curationFkField = function() {
            if (!this.length) {
                return;
            }
            var $this = (this.length > 1) ? $(this[0]) : this,
                fieldName = $this.data('fkFieldName'),
                $fkField = $this.curationField(fieldName);

            if ($fkField && $fkField.length) {
                $fkField.data('fieldName', fieldName);
                var ctFieldName = $this.data('ctFieldName');
                if (ctFieldName) {
                    $fkField.data('ctFieldName', ctFieldName);
                }
                return $fkField;
            }
        };

    })();


    /**
     * Returns either false or, if the selected option in $select points to
     * another field on the model (e.g. if the source was 'self.url'), the
     * name of the pointer field.
     */
    var getActivePointerField = function($select, toggleVisibility) {
        var previousSelectValue = $select.data('previousValue') || $select.val(),
            selectValue = $select.val(),
            oldValueData = {},
            prefix = $select.curationPrefix(),
            activePtrFieldName;

        oldValueData[previousSelectValue] = {};

        $select.find('.curated-content-type-ptr').each(function(i, option) {
            var $option = $(option);
            var ptrFieldName = $option.data('fieldName');
            var $ptrField = $('#' + prefix + ptrFieldName);
            if (!$ptrField.length) { return; }

            oldValueData[previousSelectValue][ptrFieldName] = $ptrField.val();

            if ($option.attr('value') == selectValue) {
                activePtrFieldName = ptrFieldName;
                if (toggleVisibility) {
                    $ptrField.closest('.' + ptrFieldName).andSelf().show();
                }
            } else if (toggleVisibility) {
                $ptrField.val('').closest('.' + ptrFieldName).andSelf().hide();
            }
        });
        var $fkField = $select.curationFkField();
        if ($fkField && $fkField.length) {
            $fkField.data('oldValue', $.extend(true,
                $fkField.data('oldValue') || {},
                oldValueData));
        }

        return activePtrFieldName;
    };

    // Toggle the display:block/display:none styles of form rows and
    // inputs based on the currently selected option in `select` (a generic
    // content_type field)
    var toggleContentTypeFields = function($select) {
        var selectData = $select.data();

        var prefix = $select.curationPrefix();
        if (!prefix) {
            return;
        }

        var $inlineRelated;
        if (prefix == 'id_') {
            $inlineRelated = $select.closest('fieldset');
        } else {
            var inlineRelatedId = prefix.replace(/^id_(.+)\-(\d+)\-$/, '$1$2');
            $inlineRelated = $('#' + inlineRelatedId);
        }

        // Clear out existing placeholder attributes
        $inlineRelated.find('input[placeholder],textarea[placeholder]').each(function(i, input) {
            input.removeAttribute('placeholder');
        });

        var previousSelectValue = $select.data('previousValue') || $select.val(),
            $fkField = $select.curationFkField();

        // ptrFieldSelected: Either false or, if the selected option points to
        // another field on the model (e.g. if the source was 'self.url'), the
        // name of the pointer field ('url' in the case of 'self.url').
        var ptrFieldSelected = getActivePointerField($select, true);

        // The data-old-value attribute on the generic content-type's
        // object_id field is a javascript object keyed on the select field's
        // value (i.e. the content_type_id), then the field name, e.g.:
        //
        // oldValue = {
        //      '79': {'object_id': '',    'url': 'http://www.google.com/'}
        //      '80': {'object_id': '123', 'url': ''}
        // }
        //
        // where oldValue[contentTypeId][fieldName] is equal to the value of
        // `fieldName` at the time the content_type field changed *away from*
        // that value.
        //
        // The purpose of maintaining this is that we reset the object_id
        // value (or, the pointer field's value, if the source points to an
        // internal field) when the content_type select changes. This code
        // allows the user to change content_type back and forth without
        // losing the data for that field.
        var oldValueData = {};
        oldValueData[previousSelectValue] = {};

        oldValueData[previousSelectValue][selectData.fkFieldName] = $fkField.val();
        $fkField.data('oldValue', $.extend(true,
            $fkField.data('oldValue') || {},
            oldValueData));

        if (ptrFieldSelected) {
            $fkField.hide();
            $fkField.closest('.row,.grp-row').hide();
        } else {
            $fkField.show();
            $fkField.closest('.row,.grp-row').show();
        }

        // If the content_type_id has changed to a value that was previously
        // selected and had an object_id associated with it, reset to that
        // object_id
        setTimeout(function() {
            var selectValue = $select.val(),
                oldSelectValue = $select.data('previousValue');
            $select.data('previousValue', selectValue);
            var oldValue, fieldName, $field;
            if (ptrFieldSelected) {
                fieldName = ptrFieldSelected;
                $field = $('#' + prefix + fieldName);
            } else {
                fieldName = selectData.fkFieldName;
                $field = $fkField;
            }
            oldValue = $field.val();

            var oldValueData = $fkField.data('oldValue');
            if (typeof oldValueData == 'object' && typeof oldValueData[selectValue] == 'object') {
                // If we have changed the content_type_id back to a field that
                // previously had data entered in the foreign key field or the
                // pointer field, and those fields are currently blank, restore
                // the original value.
                var newValue = oldValueData[selectValue][fieldName];
                if ($field.val() === '' && typeof(newValue) != 'undefined') {
                    $field.val(newValue);
                    // Trigger change handlers so that the title is fetched for
                    // the associated content object
                    $field.trigger('change');
                    if (!ptrFieldSelected) { // e.g. if ($field[0] == $fkField[0])
                        // return, since $fkField.onchange triggers djcuration:change,
                        // so continuing would fire the event twice
                        return;
                    }
                }
            }

            $(document).trigger('djcuration:change', [$select[0], {
                'prefix': prefix,
                'inlineRelated': $inlineRelated,
                'fieldName': fieldName,
                'field': $field,
                'fields': {
                    'fkField': $fkField,
                    'ptrField': (ptrFieldSelected) ? $field : null
                },
                'oldValue': (oldSelectValue) ? oldValue : undefined,
                'oldSelectValue': oldSelectValue
            }]);
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

        $this.data('previousValue', $this.val());

        // Bind to the focus event to store the previous value
        $this.bind("focus", function(evt) {
            var $select = $(evt.target);
            var selectValue = $select.val();
            $select.data('previousValue', selectValue);
        });
        $this.bind("change", function(evt) {
            toggleContentTypeFields($(evt.target));
        });

        // Fire djcuration:change on object_id change
        $fkField.bind("change", function(evt) {
            var $field = $(evt.target),
                prefix = $field.curationPrefix() || '',
                inlineRelatedId = prefix.replace(/^id_(.+)\-(\d+)\-$/, '$1$2'),
                $inlineRelated = $('#' + inlineRelatedId),
                $select = $field.curationCtField(),
                ptrFieldSelected = getActivePointerField($select, true),
                $ptrField = $(evt.target),
                fieldName = (ptrFieldSelected) ? ptrFieldSelected : $select.data('fkFieldName');

            $(document).trigger('djcuration:change', [$select[0], {
                'prefix': prefix,
                'inlineRelated': $inlineRelated,
                'fieldName': fieldName,
                'field': ($ptrField) ? $ptrField : $field,
                'fields': {
                    'fkField': $fkField,
                    'ptrField': $ptrField
                },
                'oldValue': undefined,
                'oldSelectValue': undefined
            }]);
        });

        // Fire djcuration:change on pointer field change
        var $select = $this,
            prefix = $select.curationPrefix() || '',
            ctFieldName = $select.data('ctFieldName');

        $this.find('.curated-content-type-ptr').each(function(i, option) {
            var $option = $(option);
            var ptrFieldName = $option.data('fieldName');
            var $ptrField = $('#' + prefix + ptrFieldName);
            if (!$ptrField.length) { return; }

            $ptrField.data('fieldName', ptrFieldName);

            $ptrField.bind('change', function(evt) {
                var $field = $(evt.target),
                    prefix = $field.curationPrefix() || '',
                    inlineRelatedId = prefix.replace(/^id_(.+)\-(\d+)\-$/, '$1$2'),
                    $inlineRelated = $('#' + inlineRelatedId),
                    $select = $('#' + prefix + ctFieldName),
                    ptrFieldSelected = getActivePointerField($select, false),
                    $ptrField = $field,
                    fieldName = (ptrFieldSelected) ? ptrFieldSelected : $select.data('fkFieldName');

                if (ptrFieldSelected == ptrFieldName) {
                    $(document).trigger('djcuration:change', [$select[0], {
                        'prefix': prefix,
                        'inlineRelated': $inlineRelated,
                        'fieldName': fieldName,
                        'field': ($ptrField) ? $ptrField : $field,
                        'fields': {
                            'fkField': $fkField,
                            'ptrField': $ptrField
                        },
                        'oldValue': undefined,
                        'oldSelectValue': undefined
                    }]);
                }
            });
        });

        // Initialize hooks into grapelli inlines
        $this.curated_related_generic();
    };

    $(document).ready(function() {
        // Iterate through curated content_type select elements
        $('.curated-content-type-select').each(function(index, element) {
            $(element).curated_content_type();
        });
    });

    // The function called by the popup window when the user clicks on a row's
    // link in the changelist for a foreignkey or generic foreign key lookup.
    //
    // It overwrites the existing function in Grapelli to trigger 'change' on
    // the related input
    window.dismissRelatedLookupPopup = function(win, chosenId, targetElement) {
        var name = windowname_to_id(win.name);
        var elem = document.getElementById(name);
        if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
            elem.value += ',' + chosenId;
        } else {
            elem.value = chosenId;
        }
        $elem = $(elem);

        // This line is the only change from Grappeli
        $elem.trigger('change');

        var title = (typeof targetElement == 'object') ? targetElement.innerHTML : null;
        win.close();
    };

})();


