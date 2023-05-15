$(document).ready(function() {
    $('.delete-btn').click(function() {
      var id = $(this).data('id');
      $('#delete-modal').show();
      $('.delete-confirm-btn').data('id', id);
    });
  
    $('.delete-cancel-btn').click(function() {
      $('#delete-modal').hide();
    });
  
    $('.delete-confirm-btn').click(function() {
      var id = $(this).data('id');
      location.href = location.href + "&parameter=" + value;
    });
  });

function setDeleteModal(deleteid){
    var id = deleteid;

    var lawyerID = document.getElementById('deletelawyerID');
    lawyerID.value = id;
}

function deleteButton(){
    var lawyerID = document.getElementById('deletelawyerID').value;
    location.href =  "/deletelawyeraccount?lawyerID=" + lawyerID;
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

function setViewModalLawyer(lawyerID, lawyer_fname, lawyer_mname, lawyer_lname, lawyer_username, lawyer_password){
   

    document.getElementById("lawyerID").value = lawyerID;
    document.getElementById("lawyerIDlabel").value = lawyerID;
    document.getElementById("lawyer_fname").value = lawyer_fname;
    document.getElementById("lawyer_mname").value = lawyer_mname;
    document.getElementById("lawyer_lname").value = lawyer_lname;
    document.getElementById("lawyer_username").value = lawyer_username;
    document.getElementById("lawyer_password").value = lawyer_password;

}


function editProfile(){
    edit = document.getElementById("edit_profile");
    cancel = document.getElementById("cancel_edit_profile");
    confirmedit = document.getElementById("confirm_edit_profile");

    lawyerID = document.getElementById("lawyerID");
    lawyer_fname = document.getElementById("lawyer_fname");
    lawyer_mname = document.getElementById("lawyer_mname");
    lawyer_lname = document.getElementById("lawyer_lname");
    lawyer_username = document.getElementById("lawyer_username");
    lawyer_password = document.getElementById("lawyer_password");


    edit.setAttribute("hidden", true);
    cancel.removeAttribute("hidden");
    confirmedit.removeAttribute("hidden");

    lawyer_fname.removeAttribute("disabled");
    lawyer_mname.removeAttribute("disabled");
    lawyer_lname.removeAttribute("disabled");
    lawyer_username.removeAttribute("disabled");
    lawyer_password.removeAttribute("disabled");


    
}

function cancelEdit(){
    location.reload();
}

function emptyEdit() {
   
    lawyer_fname = document.getElementById("lawyer_fname").value;
    lawyer_mname = document.getElementById("lawyer_mname").value;
    lawyer_lname = document.getElementById("lawyer_lname").value;
    lawyer_username = document.getElementById("lawyer_username").value;
    lawyer_password = document.getElementById("lawyer_password").value;

    if (lawyer_fname == "" || lawyer_mname == "" || lawyer_lname == "" || lawyer_username == "" || lawyer_password == "") {
        alert("Fill all the fields!");
        return false;
    };
}
