odoo.define('adm.application.student_info', require => {
    "use strict";

    require('web.core');
    const utils = require('web.utils');
    const {fileList} = require('adm.form.common');

    let partnerAvatarFile;
    let partnerPassportFile;
    let partnerResidencyPermit;

    function toggleStudentNameEdit(event) {
        $(document.getElementById('change_name_div')).toggle();
    }

    function dataURLtoFile(dataurl, filename) {

        var arr = dataurl.split(','),
            mime = arr[0].match(/:(.*?);/)[1],
            bstr = atob(arr[1]),
            n = bstr.length,
            u8arr = new Uint8Array(n);

        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }

        return new File([u8arr], filename, {type: mime});
    }

    function toggleState(countryId) {
        const $stateInput = $(document.getElementById('state_id'))
        $stateInput.children("option:gt(0)").hide().prop('disabled', true);
        $stateInput.children("option[data-country='" + countryId + "']").show().prop('disabled', false);

        if ($stateInput.children("option:selected").is(":disabled")) {
            $stateInput.children("option:nth(0)").prop("selected", true);
        }
    }

    $(document).ready(function () {
        const elAvagarPhoto = document.getElementById('avatar_photo');
        const $elAvagarPhotoFile = $(document.getElementById('avatar_photo_file'));

        const $countrySelect = $(document.getElementById('country_id'));
        $countrySelect.on('change', () => {
            toggleState($countrySelect.val());
        });
        toggleState($countrySelect.val());
        $elAvagarPhotoFile.on('input', event => {
            $(document.getElementById('student_avatar_loading')).show();
            const avatarFile = event.currentTarget.files[0];
            utils.getDataURLFromFile(avatarFile).then((base64Buffer) => {
                elAvagarPhoto.src = base64Buffer;
                partnerAvatarFile = {
                    "name": avatarFile.name,
                    "file": base64Buffer,
                    "content_type": avatarFile.type,
                }
                // Animation
                $(document.getElementById('student_avatar_loading')).hide();
                const $uploadImageSuccess = $(document.getElementById('upload_image_success'));
                $uploadImageSuccess.show();
                $uploadImageSuccess.addClass('checkmark');
                $uploadImageSuccess.delay(1500).fadeOut(1000);
                setTimeout(() => {
                    $uploadImageSuccess.removeClass('checkmark');
                }, 8000);
            });
        });

        $(document.getElementById('passport_file')).on('input', event => {
            const elFile = event.currentTarget;
            const file = elFile.files[0];
            utils.getDataURLFromFile(file).then(buffer => {
                partnerPassportFile = {
                    "name": file.name,
                    "file": buffer,
                    "content_type": file.type,
                }
            })
        });

        $(document.getElementById('passport_residency_permit')).on('input', event => {
            const elFile = event.currentTarget;
            const file = elFile.files[0];
            utils.getDataURLFromFile(file).then(buffer => {
                partnerResidencyPermit = {
                    "name": file.name,
                    "file": buffer,
                    "content_type": file.type,
                }
            })
        });

        $(document.getElementById('toggleStudentName')).on('click', toggleStudentNameEdit);
        $('.form-upload').each((i, el) => {
            const $el = $(el);
            const inputFile = $el.find('input[type=file]');
            const inputSpanLabel = $el.find('.js_input_file_label');
            inputFile.on('change', (event) => {
                inputSpanLabel.text(event.currentTarget.files[0].name);
            });
        });

        FilePond.registerPlugin(
            FilePondPluginFileEncode,
            FilePondPluginFileValidateType,
            FilePondPluginImageExifOrientation,
            FilePondPluginImagePreview,
            FilePondPluginImageCrop,
            FilePondPluginImageResize,
            FilePondPluginImageTransform,
            FilePondPluginImageEdit
        );

        const studentAvatarEl = document.getElementById('student_avatar');
        const avatarBase64 = document.getElementById('partner_avatar_base64').value;

        let imageFile = null;
        let fileOptionType = 'input';

        if (avatarBase64 !== 'data:image/*;base64,') {
            fileOptionType = 'local';
            // } else {
            imageFile = dataURLtoFile(avatarBase64, 'avatar');
        }

        const filePondAvatar = FilePond.create(studentAvatarEl, {
            files: [{
                source: '/adm/static/img/contact_photo_placeholder.png',
                options: {
                    type: fileOptionType,
                    metadata: {
                        initial: true
                    }
                },
            }],
            onupdatefiles: function (files) {
                if ((files.length && !files[0].getMetadata('initial')) || !files.length) {
                    filePondAvatar.element.dataset.admField = studentAvatarEl.dataset.admField;
                    filePondAvatar.element.dataset.admFieldType = studentAvatarEl.dataset.admFieldType;

                    fileList[studentAvatarEl.dataset.admField] = files;
                }
            },
            server: {
                process: null,
                fetch: null,
                revert: null,
                restore: null,
                load: function (source, load, error, progress, abort, headers) {
                    load(imageFile)
                    return {abort};
                }
            },
            labelIdle: `Drag & Drop your picture or <span class="filepond--label-action">Browse</span>`,
            imagePreviewHeight: 170,
            imageCropAspectRatio: '1:1',
            imageResizeTargetWidth: 200,
            imageResizeTargetHeight: 200,
            stylePanelLayout: 'compact circle',
            styleLoadIndicatorPosition: 'center bottom',
            styleButtonRemoveItemPosition: 'center bottom',
        });
    });
});