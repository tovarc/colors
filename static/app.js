if (window.location.href.includes("token")) {
  const parsedHash = new URLSearchParams(window.location.hash.substring(1));
  const token = parsedHash.get("access_token");

  fetch("/verify", {
    headers: {
      access_token: token,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        window.location.href = "/";
      }
    });
}

function changeUserColor() {
  const userColor = document.getElementById("user-color").value;

  fetch(
    "/color?" +
      new URLSearchParams({
        color: userColor,
      }),
    {
      method: "POST",
    }
  )
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
    });
}
