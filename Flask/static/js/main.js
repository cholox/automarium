/**
 * @Author: Carlos Isaza <Cholox>
 * @Date:   22-Nov-2017
 * @Project: https://github.com/cholox/automarium
 * @Last modified by:   cholox
 * @Last modified time: 10-Dec-2017
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
   var currentTemperature = '__°C';
   $('#current-temperature').html(currentTemperature);
   socket.on('mqtt_message', function(data) {
     console.log(data);
     if (data.topic.indexOf('temperature') !== -1) {
         currentTemperature = data.payload + ' °C';
         $('#current-temperature').html(currentTemperature);
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
//------------------------------------------------------------------------------
 });
