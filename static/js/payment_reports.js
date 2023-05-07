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

function setDeleteModalUser(deleteid){
    var id = deleteid;

    var paymentID = document.getElementById('deletepaymentID');
    paymentID.value = id;
}

function deleteButtonUser(){
    var paymentID = document.getElementById('deletepaymentID').value;
    location.href =  "/deletepaymentaccount?paymentID=" + paymentID;
}

function setViewModalPayment(paymentID, leasingID, pay_status, pay_lessorID, pay_lesseeID, pay_receiptNum,pay_date, pay_fee){
   

  document.getElementById("paymentID").value = paymentID;
  document.getElementById("leasingID").value = leasingID;
  document.getElementById("pay_status").value = pay_status;
  document.getElementById("pay_lessorID").value = pay_lessorID;
  document.getElementById("pay_lesseeID").value = pay_lesseeID;
  document.getElementById("pay_receiptNum").value = pay_receiptNum;
  document.getElementById("pay_date").value = pay_date;
  document.getElementById("pay_fee").value = pay_fee;

}

const paymentElement = document.getElementById("payment");
const payment = parseInt("{{payment.pay_fee}}");

paymentElement.innerText = payment.toLocaleString();