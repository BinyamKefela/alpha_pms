const title="add your own title here"; // Replace with your desired title
const amount= "add your own amount here"; // Replace with your desired amount
ma.request({
  url: this.data.baseUrl + "/create/order",
  method: "POST",
  data: {
    title: title,
    amount: amount,
  },
  success: (res) => {
    if (res.data) {
      this.startPay(res.data);
    } else {
      ma.showToast({ title: "Error: No response data received" });
    }
  },
  fail: (err) => {
    ma.showToast({ title: "Request failed: " + err.message });
  },
});

function startPay (rawRequest){
  if (!rawRequest) {
    ma.showToast({ title: "Error: Invalid payment request" });
    return;
  }

  console.log({ rawRequest: rawRequest.trim() });

  ma.startPay({
    rawRequest: rawRequest.trim(),
    success: (res) => {
      ma.showToast({ title: "Payment Result: " + res.resultCode });
    },
    fail: (err) => {
      ma.showToast({ title: "Payment failed: " + err.message });
    },
  });
}