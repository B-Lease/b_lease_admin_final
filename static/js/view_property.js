let slideIndex = [1,1];
let slideId = ["mySlides1"]
showSlides(1, 0);
showSlides(1, 1);

function plusSlides(n, no) {
  showSlides(slideIndex[no] += n, no);
}

function showSlides(n, no) {
  let i;
  let x = document.getElementsByClassName(slideId[no]);
  if (n > x.length) {slideIndex[no] = 1}    
  if (n < 1) {slideIndex[no] = x.length}
  for (i = 0; i < x.length; i++) {
     x[i].style.display = "none";  
  }
  x[slideIndex[no]-1].style.display = "block";  
}

function samePassword() {
  var x;
  x = document.getElementById("property_status").value;
 

  if (x)
  {
      alert("Are you sure you want to approve?");
      return false;
  }

}
$(document).ready(function() {
  $('.view-btn').click(function() {
    var id = $(this).data('id');
    $('#view-modal').show();
  //   $('.v\-confirm-btn').data('id', id);
  });

  $('.view-cancel-btn').click(function() {
    $('#view-modal').hide();
  });

  // $('.delete-confirm-btn').click(function() {
  //   var id = $(this).data('id');
  //   location.href = location.href + "&parameter=" + value;
  // });
});

function setUpdateModal(updateStatus){
  var id = updateStatus;

  var adminID = document.getElementById('deleteadminID');
  adminID.value = id;
}

function approveListing(propertyID){

    window.location.href = "/approveStatus?propertyID="+propertyID;

}

function declineListing(propertyID){

  
  window.location.href = "/declineStatus?propertyID="+propertyID;

}