import {apiInstance} from './instance'

export function createInvite() {
    console.log("Request Create intvite")
    const path = "/connection/new"
    return apiInstance.get(path)
}

export function checkTrusted(connectionId) {
    const path = `/connection/${connectionId}/trusted`

    return apiInstance.get(path)
}

export function createDataScientistInvite(connectionId, name, scope) {
    const path = `/connection/${connectionId}/datascientist/new`

    return apiInstance.post(path, {
        "name": name,
        "scope": scope
    })

}

export function createDataOwnerInvite(connectionId, name, domain) {
    const path = `/connection/${connectionId}/dataowner/new`

    return apiInstance.post(path, {
        "name": name,
        "domain": domain
    })

}
