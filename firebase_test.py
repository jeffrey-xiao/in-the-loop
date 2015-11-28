from firebase import firebase
firebase = firebase.FirebaseApplication('https://in-the-loop.firebaseio.com', None)

data = {
    'description': 'My description',
    'header' : 'Lillian Zhang found guilty of first degree coding',
    'tag': 'Lillian Zhang',
    'image': 'http://lorempixel.com/1280/720/sporpyts/4/',
    'data' : [
        {
            'content': 'Lillian Zhang today was found guilty by Jeffrey Xiao of commiting first degree coding. She has been sentenced to 5 years of Katherine parole.',
            'type': 'Paragraph',
            'source': {
                'name': 'CNN',
                'url': 'http://example.com'
            }
        }
    ]
}
result = firebase.post('/', data)
#firebase.delete('/users', "1")
