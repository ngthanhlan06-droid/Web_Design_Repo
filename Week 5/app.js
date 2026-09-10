async function greet() {
    return "Hello"
}

console.log(greet());

// c1
async function getData1() {
    let text = "";
    greet().then((response) => {
        text = response;
});
    return text;
}
console.log(getData1());

// c2
async function getData() {
    const text = await greet();
    return text;
}

console.log(getData());