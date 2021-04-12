import React from 'react'
import {createDataOwnerInvite} from "./api/connections";

const DataOwnerTab = ({connectionId}) => {

    let [name, setName] = React.useState("")
    let [domain, setDomain] = React.useState("")
    let [invitation, setInvitation] = React.useState(null)


    function createInvitation(event) {
        event.preventDefault()
        createDataOwnerInvite(connectionId, name, domain).then(response => {
            console.log("Invitation : ", response.data.invitation)
            setInvitation(JSON.stringify(response.data.invitation))
        }).catch(error => {
            console.log("Error : ", error)
        })
    }


    return (
        <div>
            <h2>Create Data Owner Invitation</h2>
            <p>By accepting this invitation in the DataOwner Notebook, you will automatically be issued a credential with the following attributes. Fill them in however you like.</p>
            <form onSubmit={createInvitation}>
                <div><label>Name : </label><input value={name} onChange={(e) => setName(e.target.value)}/></div>
                <div><label>Domain of Data</label><input value={domain} onChange={(e) => setDomain(e.target.value)}/></div>
                <button type="submit">Generate Invitation</button>
            </form>

            {invitation && (
                <div>
                    <h2>Data Owner Invite</h2>
                    <h3>Copy This</h3>
                    <textarea readOnly={true} value={invitation}/>
                </div>
            )}

        </div>
    )
}

export default DataOwnerTab
