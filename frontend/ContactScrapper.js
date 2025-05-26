import React, { useState } from 'react';
import { View, Button, FlatList, Text, Alert } from 'react-native';
import * as Contacts from 'expo-contacts';

export default function ContactScraper({ onContactsReady }) {
  const [contacts, setContacts] = useState([]);
  const [status, setStatus] = useState('Idle');

  const fetchContacts = async () => {
    const { status } = await Contacts.requestPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission denied to access contacts');
      return;
    }

    setStatus('Loading...');
    const { data } = await Contacts.getContactsAsync({
      fields: [Contacts.Fields.PhoneNumbers, Contacts.Fields.Emails],
    });

    const cleaned = data
      .filter(c => c.name)
      .map(contact => ({
        name: contact.name,
        phone: contact.phoneNumbers?.[0]?.number || null,
        email: contact.emails?.[0]?.email || null,
        profession: null,
        tags: [],
        source: 'phone'
      }));

    setContacts(cleaned);
    onContactsReady(cleaned);  // ⬅️ pass to parent for backend upload
    setStatus(`Imported ${cleaned.length} contacts`);
  };

  return (
    <View style={{ padding: 20 }}>
      <Button title="Import Phone Contacts" onPress={fetchContacts} />
      <Text style={{ marginTop: 10 }}>{status}</Text>
      <FlatList
        data={contacts}
        keyExtractor={(_, index) => index.toString()}
        renderItem={({ item }) => (
          <Text style={{ marginVertical: 2 }}>{item.name} | {item.email || 'No email'}</Text>
        )}
      />
    </View>
  );
}
