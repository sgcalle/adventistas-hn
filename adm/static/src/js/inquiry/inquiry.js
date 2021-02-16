odoo.define('adm.inquiry', require => {
    "use strict"
    // TODO: Make this script work with Widgets

    // We just wait to some things to be done before using JQuery :)
    // This can be unneeded if we drop JQuery in this module (I hope some day...)
    require('web.core');

    let studentCount = 1;

    function recomputaTabStudent() {
        $('#studentsNavbar').find('li').each((i, el) => {
            const $el = $(el);
            $el.children('a.student').html('Student '+(i+1)+'');
        });
        $('#studentsNavbar').find('li > a.student').last().click();
        $('#studentsCount').val($('#studentsNavbar').find('li > a').length-1);
    }
    function removeStudent(idStudent) {
        $(`#navStudent${idStudent}`).remove();
        $(`#student${idStudent}`).remove();
        recomputaTabStudent();
    }

    function addStudent() {
        studentCount++;
        var htmlTab =
            `<li class="nav-item" style="position: relative" id="navStudent${studentCount}">
        <a class="nav-link student" id="student${studentCount}-tab" data-toggle="tab" href="#student${studentCount}"
            role="tab" aria-controls="student${studentCount}" aria-selected="false">Student ${studentCount}</a>
            <i data-tabRemove="${studentCount}" class="fa fa-times remove-tab" style="position: absolute; top: -0.5em; right: 0.1em; font-size: 1.4em; color: orangered; cursor: pointer;""></i>
    </li>`;


        $(htmlTab).insertBefore($(this).parent());

        $('#studentsCount').val(studentCount);

        var studentClonnable = document.getElementById("student1").cloneNode(true);
        var studentTabContent = document.getElementById("studentsTabContent");

        studentTabContent.appendChild(studentClonnable);

        // Reassign ids
        $(studentClonnable).attr("id", "student" + studentCount);
        $(studentClonnable).attr("aria-labelledby", "student" + studentCount + "-tab");
        $(studentClonnable).removeClass("active");
        $(studentClonnable).removeClass("show");

        $(studentClonnable).find('input[id]').each((i, el) => {
            const $el = $(el);
            const newId = el.id + '-' + studentCount;
            $(studentClonnable).find(`label[for=${el.id}]`).attr('for', newId);
            el.id = newId
        });
//        $(studentClonnable).find("#txtStudent1FirstName").attr("id", "txtStudent" + studentCount + "FirstName")
//        $(studentClonnable).find("#txtStudent1MiddleName").attr("id", "txtStudent" + studentCount + "MiddleName")
//        $(studentClonnable).find("#txtStudent1LastName").attr("id", "txtStudent" + studentCount + "LastName")
//        $(studentClonnable).find("#txtStudent1Birthday").attr("id", "txtStudent" + studentCount + "Birthday")
//        $(studentClonnable).find("#selStudent1Gender").attr("id", "selStudent" + studentCount + "Gender")
//        $(studentClonnable).find("#selStudent1Nativelanguage").attr("id", "selStudent" + studentCount + "Nativelanguage")
//        $(studentClonnable).find("#selStudent1SchoolYear").attr("id", "selStudent" + studentCount + "SchoolYear")
//        $(studentClonnable).find("#selStudent1GradeLevel").attr("id", "selStudent" + studentCount + "GradeLevel")
//        $(studentClonnable).find("#selStudent1CurrentGradeLevel").attr("id", "selStudent" + studentCount + "CurrentGradeLevel")
//        $(studentClonnable).find("#txtStudent1CurrentSchool").attr("id", "txtStudent" + studentCount + "CurrentSchool")
//        $(studentClonnable).find("#txtStudent1FromEnglishSchool").attr("id", "txtStudent" + studentCount + "FromEnglishSchool")
//        $(studentClonnable).find("#txtStudent1FromEnglishSchool").attr("label", "txtStudent" + studentCount + "FromEnglishSchool")
//        $(studentClonnable).find(".txtStudent1ExtraServices").attr("name", "txtStudent" + studentCount + "ExtraServices")
//        $(studentClonnable).find(".txtStudent1ExtraServices").attr("id", "txtStudent" + studentCount + "ExtraServices")
//        $(studentClonnable).find("#fileStudent1Photo").attr("name", "fileStudent" + studentCount + "Photo")
//        $(studentClonnable).find("#fileStudent1BirthCert").attr("name", "fileStudent" + studentCount + "BirthCert")
//        $(studentClonnable).find("#fileStudent1ReportCard").attr("name", "fileStudent" + studentCount + "ReportCard")
//        $(studentClonnable).find("#fileStudent1ImmunizationRecord").attr("name", "fileStudent" + studentCount + "ImmunizationRecord")

        $(studentClonnable).find("input").each(function () {
            var input_type = $(this).attr("type")
            if (input_type == "checkbox") {
                this.checked = false
            } else {
                $(this).val("");
            }
        });


        document.querySelectorAll(".selectSchoolYear").forEach(function (element) {
            element.addEventListener("change", function () {
                var schoolCodeID = $(this).find("option:selected").data("school_code");
                $(this).parent().next().find("select option").each(function (element) {
                    var school_option_id = $(this).data("school_code");
                    if (schoolCodeID != -1 && schoolCodeID == school_option_id)
                        $(this).removeClass('d-none')
                    else
                        $(this).addClass('d-none')
                })
                $(this).parent().next().find("select").val(-1);
            })
        });
        recomputaTabStudent();
    }

    function showOnlyCountrysStates() {
        // You might ask, why don't use # selector instead of getElementById
        // The reason for that is getElementById uses native code, so is much faster
        // And passing to jquery an element, it doesn't try to find it.
        // So... $(getElementById) has better performance and allow us to use JQuery :)

        const selectState = $(document.getElementById('selState'));
        const selectCountry = document.getElementById('selCountry');

        selectState.children("option:gt(0)").hide();
        selectState.children("option[data-country='" + selectCountry.value + "']").show();

        if (selectState.children("option:selected").is(":hidden")) {
            selectState.children("option:nth(0)").prop("selected", true);
        }
    }

    function hideDataParents() {
        $(".hide_parent").toggle();
        $("#input_family_id").toggle();

        if ($("#checkbox_family_id").prop("checked"))
            $("#section_parent_2").hide()

        if ($(".hide_parent").css("display") == "none") {
            $(".hide_parent input").attr("disabled", true);
            $(".hide_parent select").attr("disabled", true);
        } else {
            $(".hide_parent input").attr("disabled", false);
            $(".hide_parent select").attr("disabled", false);
        }

        if ($("#input_family_id").css("display") == "none")
            $(".input_family_id input").attr("disabled", true);
        else
            $(".input_family_id input").attr("disabled", false);

    }

    function toggleSecondParent() {
        $("#section_parent_2").toggle();

        if ($("#section_parent_2").css("display") == "none") {
            $("#section_parent_2 input").attr("disabled", true);
            $("#section_parent_2 select").attr("disabled", true);
        } else {
            $("#section_parent_2 input").attr("disabled", false);
            $("#section_parent_2 select").attr("disabled", false);
        }
    }

    function invoiceAddress(valor) {
        var status = valor.data
        if(status == 1){
            $("input[name='txtInvoiceAddress_1']").prop("checked", true);
            $("input[name='txtInvoiceAddress_2']").prop("checked", false);
        }else{
            $("input[name='txtInvoiceAddress_1']").prop("checked", false);
            $("input[name='txtInvoiceAddress_2']").prop("checked", true);
        }

    }

    $(document).ready(function () {

        // Format Init data :P
        showOnlyCountrysStates();

        // Event Handlers
        //document.getElementById("add-tab").addEventListener("click", addStudent);
        document.getElementById("selCountry").addEventListener("change", showOnlyCountrysStates);

        document.getElementById('showSecondParent').addEventListener('click', toggleSecondParent);

        $('#checkbox_family_id').on('click',hideDataParents)
        $('#txtInvoiceAddress_1').click(1,invoiceAddress)
        $('#txtInvoiceAddress_2').click(2,invoiceAddress)

        $('#add-tab').on('click',addStudent)

        $(document).on('click', '.remove-tab', function () {
            removeStudent($(this).attr('data-tabRemove'))
        });


        document.querySelectorAll(".custom-file-input").forEach(function (element) {
            element.addEventListener("change", function () {
                var fileName = this.files[0].name
                $(this).next("label").text(fileName);
            })
        })
        document.querySelectorAll(".selectSchoolYear").forEach(function (element) {
            element.addEventListener("change", function () {
                var schoolCodeID = $(this).find("option:selected").data("school_code");
                $(this).parent().next().find("select option").each(function (element) {
                    var school_option_id = $(this).data("school_code");
                    if (schoolCodeID != -1 && schoolCodeID == school_option_id)
                        $(this).removeClass('d-none')
                    else
                        $(this).addClass('d-none')
                })
                $(this).parent().next().find("select").val(-1);
            })
        });
//        document.querySelectorAll(".selStudentSchoolCode").forEach(function (element) {
//            element.addEventListener("change", function () {
//                var schoolCodeID = $(this).find("option:selected").data("school_code");
//                $(this).parent().next().find("select option").each(function (element) {
//                    var school_option_id = $(this).data("school_code");
//                    if (schoolCodeID != -1 && schoolCodeID == school_option_id)
//                        $(this).removeClass('d-none')
//                    else
//                        $(this).addClass('d-none')
//                })
//                $(this).parent().next().find("select").val(-1);
//            })
//        });
        document.querySelectorAll("#selSource").forEach(function (element) {
            element.addEventListener("change", function () {
                if ($(this).find("option:selected").data("other") != undefined)
                    $("#contOtherSource").removeClass("d-none")
                else
                    $("#contOtherSource").addClass("d-none")
            })
        });
    });

    // Get user location
    $.get('/adm/geolocation').then(result => {
        if (!_.isEmpty(result)) {
            // Country
            const selCountry = document.getElementById("selCountry");
            const countryOption = _.filter(selCountry.options, option => option.dataset.code === result.country_code)
            if (countryOption.length) {
                selCountry.value = countryOption[0].value;

                // State
                const selState = document.getElementById("selState");
                const stateOption = _.filter(selCountry.options, option => option.dataset.country === countryOption[0].value
                                             && option.dataset.code === result.region)
                if (stateOption.length) {
                    selState.value = stateOption[0].value;
                }
            }
            showOnlyCountrysStates();
        }
    })
})
