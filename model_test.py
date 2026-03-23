import requests
import json


url = "http://localhost:11434/api/chat"

text = '''
You are an expert summarizer that produces concise, clear, and accurate summaries of paragraphs while preserving the key ideas and tone of the original text.

Summarize the following paragraph in a clear and coherent manner.

# Instructions
1. Focus only on the main ideas and essential information.
2. Remove redundant phrases or examples.
3. Use neutral, professional language.
4. The summary should be no longer than 3–4 sentences, and under 100 characters.
5. Emphasize on details

# Input Paragraph
A workation is a fantastic idea – it allows you to combine work with relaxation and helps you maintain a better balance between work and personal life. I understand your concerns about Himachal and Uttarakhand, especially since temperatures there can drop significantly in winter, and some areas can get snowy, which might impact accessibility and travel comfort.

If you are still considering the mountains, think about Jibhi – it is a less crowded, picturesque place in Himachal Pradesh, where it is a bit warmer than in the higher mountain regions. Jibhi offers beautiful views and a peaceful atmosphere, perfect for a workation. You can enjoy local cuisine, take calm hikes, and find cozy cafes that provide a comfortable setting for work. Another mountain option with decent temperatures is Bir Billing. Bir Billing is famous for its scenic views and is known as a paragliding hub – even if you’re not into adventure sports, you can watch the paragliders and relax in this unique atmosphere. Bir offers peace, local cafes and restaurants, and the chance to meet interesting people from around the world, which makes it easy to settle in as a solo traveler.

Additionally, Bir has excellent spots for meditation and yoga, and the local community is very welcoming, giving you the chance to experience local traditions and cuisine. It is a great place if you are looking for a balance between tranquility and the opportunity to join local events and gatherings.

Another good option is Udaipur. Warmer than the mountains, Udaipur has its own unique charm with lakes, stunning palaces, and many places to meet locals. After work, it is worth taking a stroll by Lake Pichola to enjoy the city beauty and explore its rich culture.

Among digital nomads, Goa is also extremely popular. At this time of year, it is not as hot or crowded as during peak season. Goa has excellent infrastructure for remote work, with plenty of coworking spaces and cafe-style workplaces, making it easy to organize your work and relaxation schedule.

For remote work, reliable internet access will be essential, so I recommend checking out https://www.tripoffice.com/ It is a search engine dedicated to digital nomads, where you can find accommodations with comfortable desks, stable Wi-Fi, and other work-friendly amenities across various price ranges.

Wishing you a great trip and good luck with your workation!
'''

data = {
    "model": "granite3.2:2b",
    "messages": [
        {"role": "user", "content": f"{text}"}
    ]
}

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    print('Streaming Response')
    print('-' * 100)
    for line in response.iter_lines(decode_unicode=True):
        if line:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    print(data['message']['content'], end='', flush=True)
            except json.JSONDecodeError:
                print(f'Failed to parse the {line}')
    print('\n')
else:
    print(f'Error: {response.status_code}')
    print(response.text)