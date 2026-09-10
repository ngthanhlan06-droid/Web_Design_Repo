let posts = document.querySelectorAll("card");

let arr= []

for (let i = 0; i < posts.length; i++) {
    let title = post [i].querySelector("h2");
    let content = post [i].querySelector("p");

    let post ={
        title: title.textContent,
        content: content.textContent.trim(),
    };

    arr.push(post);
    //console.log("Content:", content.textContent.trim());

    title.textContent = "Bai viet so " + (i + 1);
    title.style.color = "red";
}

console.log(arr);