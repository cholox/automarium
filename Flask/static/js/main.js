/**
 * @Author: Carlos Isaza <Cholox>
 * @Date:   22-Nov-2017
 * @Project: https://github.com/cholox/automarium
 * @Last modified by:   Carlos Isaza
 * @Last modified time: 18-Dec-2017
 * @License: MIT
 */


 $(document).ready(function() {

   var socket = io.connect('http://' + document.domain + ':' + location.port);
   $('#change_light_schedule').click(function(event) {
     var light_time1 = $('#light_time1').val();
     var light_time2 = $('#light_time2').val();
     var data = {time1: light_time1, time2: light_time2};
     if (light_time1 != "" && light_time2 != "") {
        socket.emit('change_light_schedule', data=JSON.stringify(data));
    }
   });
   $('#change_co2_schedule').click(function(event) {
     var co2_time1 = $('#co2_time1').val();
     var co2_time2 = $('#co2_time2').val();
     var data = {time1: co2_time1, time2: co2_time2};
     if (co2_time1 != "" && co2_time2 != "") {
        socket.emit('change_co2_schedule', data=JSON.stringify(data));
     }
   });
   $('#change_fertilizer_schedule').click(function(event) {
     var fertilizer_time = $('#fertilizer_time').val();
     var fertilizer_amount = $('#fertilizer_amount').val();
     var data = {time: fertilizer_time, amount: fertilizer_amount};
     if (fertilizer_time != "" && fertilizer_amount != ""){
        socket.emit('change_fertilizer_schedule', data=JSON.stringify(data));
     }
   });
   var currentTemperature = '';
   $('#current-temperature').html(currentTemperature);
   socket.on('mqtt_message', function(data) {
     console.log(data);
     if (data.topic.indexOf('temperature') !== -1) {
         currentTemperature = data.payload + ' °C';
         $('#current-temperature').html(currentTemperature);
     }
   });
   $('#change_relay2_schedule').click(function(event) {
     var relay2_time1 = $('#relay2_time1').val();
     var relay2_time2 = $('#relay2_time2').val();
     var data = {time1: relay2_time1, time2: relay2_time2};
     if (relay2_time1 != "" && relay2_time2 != "") {
        socket.emit('change_relay2_schedule', data=JSON.stringify(data));
    }
   });

   socket.on('connect', function(data) {
     console.log('Connected');
   });
//------------------------------Direct Commands---------------------------------
$('#turn_lights_on_button').click(function(event) {
    socket.emit('turn_lights_on');
});
$('#turn_lights_off_button').click(function(event) {
    socket.emit('turn_lights_off');
});
$('#turn_relay2_on_button').click(function(event) {
    socket.emit('turn_relay2_on');
});
$('#turn_relay2_off_button').click(function(event) {
    socket.emit('turn_relay2_off');
});
$('#turn_motor_on_button').click(function(event) {
    socket.emit('turn_motor_on');
});
$('#turn_motor_off_button').click(function(event) {
    socket.emit('turn_motor_off');
});
$('#fertilize_secs_button').click(function(event) {
    var fertiliAmount = $('#fertilize_secs_amount_test').val()
    if (fertiliAmount != "") {
        socket.emit('fertilize_secs', data=JSON.stringify({amount: fertiliAmount}));
    }
});
$('#open_co2_button').click(function(event) {
    socket.emit('open_co2');
});
$('#close_co2_button').click(function(event) {
    socket.emit('close_co2');
});
//------------------------------------------------------------------------------
 });
