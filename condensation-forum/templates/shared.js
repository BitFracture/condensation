/**
* Allows an iFrame to grow to its contents after they load.
*/
function resizeIframe(obj) {
    obj.style.height = obj.contentWindow.document.body.scrollHeight + 'px';
}

/**
* Unhides the attachment frame.
*/
function startAttachment() {
    document.getElementById("attach-frame").style.display = "block";
    document.getElementById('attach-iframe').src += '';
};

/**
* Add a number to the JSON array string. Uniqueness is enforced.
*/
function selectAttachment(number, fileName) {

    document.getElementById("attach-frame").style.display = "none";

    var formElement = document.getElementById('fileIds');
    var currentList = JSON.parse(formElement.value);
    for (var i = 0; i < currentList.length; i++) {
        if (number == currentList[i]["id"]) return;
    }
    currentList.push({"id": number, "name": fileName});
    formElement.value = JSON.stringify(currentList);

    loadAttachmentList();
}

/**
* Remove a number from the JSON array string
*/
function unselectAttachment(number) {

    document.getElementById("attach-frame").style.display = "none";

    var formElement = document.getElementById('fileIds');
    var currentList = JSON.parse(formElement.value);
    for (var i = 0; i < currentList.length; i++) {

        if (number == currentList[i]["id"]) {
            currentList.splice(i, 1);
            break;
        }
    }
    formElement.value = JSON.stringify(currentList);

    loadAttachmentList();
}

/**
* Renders the markup for the visible attachment list. Note that the actual attachment form input is actually stored
* with selectAttachment.
*/
function loadAttachmentList() {

    var formElement = document.getElementById('fileIds');
    var currentList = JSON.parse(formElement.value);
    var rendered = "";
    for (var i = 0; i < currentList.length; i++) {
        rendered += '<button type="button" class="list-group-item list-group-item-action" ';
        rendered += 'onclick="unselectAttachment(' + currentList[i]["id"] + ')" >';
        rendered += currentList[i]["name"] + '</button>';
    }
    rendered += '<button type="button" class="list-group-item list-group-item-action active" style="width: auto;" '
    rendered += 'onclick="startAttachment();" >';
    rendered += 'Attach A File</button>'

    document.getElementById("fileList").innerHTML = rendered;
}
