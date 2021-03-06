$(function () {
    // Bulk delete-full selection
    $("#checkall-bottom").change(function () {
        var isCheckAll = $(this).is(":checked");
        if (isCheckAll) {
            $(".menu-item").prop("checked", true);
        } else {
            $(".menu-item").prop("checked", false);
        }
    });

    //Bulk delete-submit
    $("#batchDelete").click(function () {
        var uri = $(this).data('uri');
        var idList = $("input:checkbox:checked.menu-item").map(function () {
            return $(this).data('id')
        }).get();
        if (!idList.length) {
            swal({
                title: gettext('Please select the data to delete'),
                type: "warning",
                confirmButtonColor: "#1ab394"
            });
            return false
        }
        swal({
            title: gettext('Are you sure you want to delete it'),
            type: "warning",
            allowOutsideClick: true,
            showCancelButton: true,
            confirmButtonColor: "#ff6700",
            confirmButtonText: gettext('delete'),
            cancelButtonText: gettext('cancel'),
            closeOnConfirm: false
        }, function () {
            $.ajax({
                url: uri,
                data: {
                    'ids': idList.join(','),
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                dataType: "json",
                type: "POST",
                success: function (resp) {
                    if (resp.state) {
                        window.location.reload();
                    } else {
                        var error = resp.error;
                        swal({
                            title: error,
                            confirmButtonColor: "#1ab394"
                        });
                    }
                },
                error: function (err) {
                    if (err.statusText !== 'abort') {
                        swal({
                            title: gettext('Oops, something went wrong'),
                            type: "error",
                            confirmButtonColor: "#1ab394"
                        });
                    }
                }
            });
        });
    });
});