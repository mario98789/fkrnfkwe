async def search_via_searcheebot(session_path, keyword_list):
    client = TelegramClient(session_path, api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
    await client.start()

    found_links = set()
    bot = await client.get_entity("@SearcheeBot")

    for keyword in keyword_list:
        st.markdown(f"🔍 <b>Запрос:</b> <code>{keyword}</code>", unsafe_allow_html=True)
        await client.send_message(bot, keyword)
        await asyncio.sleep(4)

        messages = await client.get_messages(bot, limit=30)
        if not messages:
            st.warning("⚠️ Бот не ответил.")
            continue

        got_links = False
        for msg in messages:
            if msg.message:
                st.code(msg.message[:300], language="text")  # покажем часть ответа
                links = re.findall(r'https://t\.me/[^\s\)]+', msg.message)
                if links:
                    got_links = True
                    found_links.update(links)

        if not got_links:
            st.info("ℹ️ Ответ получен, но без ссылок.")

        # Нажмём “More”
        for i in range(5):
            await client.send_message(bot, "More")
            await asyncio.sleep(3)
            more_messages = await client.get_messages(bot, limit=20)
            for msg in more_messages:
                if msg.message:
                    links = re.findall(r'https://t\.me/[^\s\)]+', msg.message)
                    if links:
                        found_links.update(links)

    await client.disconnect()
    return sorted(found_links)
