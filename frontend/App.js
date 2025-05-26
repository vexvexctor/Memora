import React, { useState } from 'react';
import { ScrollView, View, Text, Button, Alert } from 'react-native';
import ContactScraper from './ContactScraper';
import GmailOAuth from './GmailOAuth';
import SearchComponent from './SearchComponent';

export default function App() {
  const [contacts, setContacts] = useState([]);
  const [gmailContacts, setGmailContacts] = useState([]);
  const [uploaded, setUploaded] = useState(false);
  const BACKEND_URL = 'http://192.168.1.248:8000'; // 🔁 Replace with your local IP

  const handleUpload = async () => {
    const combined = [...contacts, ...gmailContacts];

    if (combined.length === 0) {
      Alert.alert('No contacts to upload!');
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/upload_contacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contacts: combined,
          query_tags: [] // optional initial tag list
        })
      });
      const json = await res.json();
      console.log(json);
      setUploaded(true);
      Alert.alert(`Uploaded ${combined.length} contacts!`);
    } catch (err) {
      console.error(err);
      Alert.alert('Upload failed. Check backend connection.');
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 10 }}>
        AI Contact Graph
      </Text>

      <ContactScraper onContactsReady={setContacts} />
      <GmailOAuth onEmailsReady={setGmailContacts} />

      <Button
        title="Upload Contacts to Backend"
        onPress={handleUpload}
        color="#4682B4"
      />

      {uploaded && (
        <View style={{ marginTop: 30 }}>
          <SearchComponent />
        </View>
      )}
    </ScrollView>
  );
}
