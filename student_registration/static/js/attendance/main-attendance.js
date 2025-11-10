
$(document).ready(
   function()
   {
        if($(document).find('#id_attendance_date').length == 1) {
            $('#id_attendance_date').datepicker({dateFormat: "yy-mm-dd"});
        }

//      show reason if day_off is yes
        day_off = $("#id_day_off").val();
        $('div#div_id_close_reason').addClass('d-none');
        if (day_off == 'yes') {
            $('div#div_id_close_reason').removeClass('d-none');
        }
        else
        {
        $('div#div_id_close_reason').addClass('d-none');
        }

//      Default Setting: close_reason is hidden
        $(document).on('change', 'select#id_day_off', function () {
            $('div#div_id_close_reason').addClass('d-none');
            day_off = $("#id_day_off").val();
            if (day_off == 'yes') {
                $('div#div_id_close_reason').removeClass('d-none');
            }
            else {
                $('div#div_id_close_reason').addClass('d-none');
            }
        });


      $("#button-id-loadstudentsbutton").click(function() {
          load_students();
      });



   }
);

function load_students()
 {
    schoolID = $("#id_school").val();
    registrationLevel = $("#id_registration_level").val();
    day_off = $("#id_day_off").val();
    attendance_date = $("#id_attendance_date").val();
    if (schoolID>0 && registrationLevel!='' )
    {
        if(day_off=='yes')
        {
            close_reason = $("#id_close_reason").val();
            if (close_reason!='')
            {
                window.location = window.location.origin
                + "/attendances/main-attendance/?attendance_date="+attendance_date.toString()
                +"&school="+schoolID.toString()
                +"&registration_level="+registrationLevel.toString()
                +"&day_off="+day_off.toString()
            }
            else
            {
                showModal("Please specify the reason for day off");
            }
        }
        else
        {
            window.location = window.location.origin
            + "/attendances/main-attendance/?attendance_date="+attendance_date.toString()
            +"&school="+schoolID.toString()
            +"&registration_level="+registrationLevel.toString()
            +"&day_off="+day_off.toString()
            ;
        }
    }
    else
    {
        showModal("School and Registration Level are mandatory")
    }

 }

function disableHoliday(date) {
    var string = $.datepicker.formatDate('yy-mm-dd', date);

    var filterDate = new Date(string);
    var day = filterDate.getDay();
    return [day != 0 && day !=6]
 }


