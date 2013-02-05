function show_detail(scene_name)
{
$.ajax({
  type:'GET',
  url:'/scene/get_scene_detail',
  async:false,
  data: ({scene_name:scene_name}),
  success:function(data){
   $('#scene_detail').html(data)},
  dataType:"text"
});
}
function watch_pid()
{
  $.ajax({
  type:'POST',
  url:'/scene/watch',
  async:true,
  data: ({watch_host:$("#watch_host").val()}),
  success:function(data){
   $('#ps').html(data)},
  dataType:"text"
});
}
function check_pids()
{
  $.ajax({
  type:'POST',
  url:'/scene/check_pids',
  async:true,
  data: ({watch_host:$("#watch_host").val()}),
  success:function(data){
   $('#res').html(data)},
  dataType:"text"
});
}

function restart(k, gsid)
{
$.ajax({
  type:'POST',
  url:'/scene/restart',
  async:false,
  data: ({k:k, gsid:gsid}),
  success:function(data){
   $('#res').html(data)},
  dataType:"text"
});
location.reload();
}
