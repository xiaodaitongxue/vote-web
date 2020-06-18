
    $(function () {
        $('.good').click(function () {
            // console.log(666)
            var $add = $(this)
            var gno=$add.attr('gno')
            // console.log(gno)

            $.getJSON('/vote/addtogood',{'gno':gno}, function (data) {
                console.log(data)
                if (data['status'] === 302) {
                    window.open('/vote/login/', target = "_self");
                } else if (data['status'] === 200) {
                    $add.next('span').html(data['teacher.good_count']);
                }

            })

        })

        $('.bad').click(function () {
            var $add = $(this)
            var bno=$add.attr('bno')
            // console.log(bno)

            $.getJSON('/vote/addtobad',{'bno':bno}, function (data) {
                console.log(data)
                if (data['status'] === 302) {
                    window.open('/vote/login/', target = "_self");
                } else if (data['status'] === 200) {
                    $add.next('span').html(data['teacher.bad_count']);
                }

            })

        })
    })


    // $(function () {
    //     $('.good').click(function () {
    //         var $add = $(this)
    //         var gno=$add.attr('gno')
    //
    //         $.get('/vote/praise',{'gno':gno}, function (data) {
    //             if (data['status'] === 302) {
    //                 window.open('/vote/login/', target = "_self");
    //             } else if (data['status'] === 200) {
    //                 $add.next('span').html(data['teacher.good_count']);
    //             }
    //
    //         })
    //
    //     })
    //
    //     $('.bad').click(function () {
    //         var $add = $(this)
    //         var bno=$add.attr('bno')
    //         console.log(bno)
    //
    //         $.get('/vote/criticize',{'bno':bno}, function (data) {
    //             if (data['status'] === 302) {
    //                 window.open('/vote/login/', target = "_self");
    //             } else if (data['status'] === 200) {
    //                 $add.next('span').html(data['teacher.bad_count']);
    //             }
    //
    //         })
    //
    //     })
    // })

