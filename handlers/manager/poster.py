import time

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from bot.start_bot_container import bot
from bot_data import config
from db import functions as db
from db.models import Channel, Manager, ManagerPlacement, PostInfo, ChannelConfiguration, Schedule, DictObject, Dict, \
	PostTime
from keyboards import inline
from . import templates, utils

from states import manager as states

from .main import manager_handler
from .utils import convert_message, next_message_exists, send_message_dicts


async def poster_handler(message: types.Message, state: FSMContext):
	channels = Manager.select().where(Manager.admin_id == message.from_user.id)
	channels = [await bot.get_chat(i.channel_id) for i in channels]
	await message.answer(templates.poster_1_message, reply_markup=templates.poster_send_channel_menu(channels))
	await state.set_state(states.Poster.sendChannel)

async def poster_choose_channel_handler(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	await call.message.delete()
	await call.message.answer(templates.poster_2_message, reply_markup=templates.poster_reply_menu())
	await state.set_state(states.Poster.sendClientName)
	channel = Channel.get(channel_id=channel_id)
	await state.update_data(channel_id=channel.id)


async def send_client_name_handler(message: types.Message, state: FSMContext):
	await state.update_data(client_name=message.text)

	await message.answer(templates.poster_3_message)

	await state.set_state(states.Poster.sendPost)

async def cancel_poster_handler(message: types.Message, state: FSMContext):
	await manager_handler(message, state)


async def send_post_poster_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if data.get('start_message_id') is None:
		data['start_message_id'] = 0
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])
	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)

	if not await next_message_exists(message):
		data = await state.get_data()
		if data.get('album_message'):
			return
		mess = await send_message_dicts(dicts, message.chat.id)
		p = PostInfo.create()

		mes =  await message.answer(templates.album_edit_message, reply_markup=templates.poster_send_post_menu(context=p.id),
									disable_web_page_preview=True)
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		await state.update_data(info=p.id, active=True, post_message_id=post_message_id, album_message=mes.message_id,
								post_message=mess)

		await state.set_state(states.Poster.settingPost)


		for mes in data.pop('mess'):
			await mes.delete()


async def poster_swap_comments_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	channel = Channel.get(id=data['channel_id'])
	chat = await bot.get_chat(channel.channel_id)
	if not chat.linked_chat_id:
		await bot.answer_callback_query(call.id, 'Комментарии на канале отключены!')
		return
	try:
		members = await bot.get_chat_member_count(chat.linked_chat_id)
	except Exception:

		await bot.answer_callback_query(call.id, f'Добавьте бота в группу!', show_alert=True)
		return
	config = ChannelConfiguration.get(channel_id=channel.channel_id)
	config.linked_chat_id = chat.linked_chat_id
	config.save()
	p = PostInfo.get(id=data['info'])
	p.with_comment = not p.with_comment
	p.save()
	await call.message.edit_reply_markup(reply_markup=templates.poster_send_post_menu(context=p.id))


async def poster_change_price_handler(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Poster.sendPrice)
	mes = await call.message.answer(templates.send_changed_price_message, reply_markup=templates.only_back())
	await state.update_data(message_to_delete=[mes.message_id])


async def back_poster_change_price_handler(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await state.update_data(message_to_delete=None)
	await state.set_state(states.Poster.settingPost)


async def poster_send_changed_price_handler(message: types.Message, state: FSMContext):
	text = message.text

	await bot.delete_message(message.chat.id, message.message_id)

	if not message.text.isdigit():
		await message.answer('Ошибка! Это не число')
		return

	data = await state.get_data()

	p = PostInfo.get(id=data['info'])
	p.price = int(text)
	p.save()

	await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=data['album_message'],
										reply_markup=templates.poster_send_post_menu(context=p.id))

	deleted = True
	i = 1
	while deleted:
		try:
			await bot.delete_message(message.chat.id, message.message_id - i)
			deleted = False
		except Exception:
			i += 1

	await state.set_state(states.Poster.settingPost)


async def poster_cancel(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.delete()
	await call.message.answer(templates.manager_text, reply_markup=templates.manager_menu())

async def poster_next_post(call: types.CallbackQuery, state: FSMContext):
	data: dict = await state.get_data()

	p = PostInfo.get(id=data['info'])

	if not p.price:
		await bot.answer_callback_query(call.id, 'Укажи цену, это же коммерческое размещение!', show_alert=True)
		return

	await  state.set_state(states.Poster.sendTime)
	await state.update_data(post_date=0, date=0, message_id=call.message.message_id)
	data = await state.get_data()
	await call.message.edit_text(templates.poster_postpone_message, reply_markup=inline.postpone(data))

async def poster_postpone_back_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await call.message.delete()
	await state.set_state(states.Poster.settingPost)
	await state.update_data(post_date=None, date=None, message_id=None)

	mes = await call.message.answer(templates.album_edit_message,
							   reply_markup=templates.poster_send_post_menu(context=data['info']),
							   disable_web_page_preview=True)



async def poster_swap_keyboard(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Poster.sendKeyboard)
	mes = await call.message.answer(templates.poster_swap_keyboard_message, reply_markup=templates.only_back())
	await state.update_data(message_id=[call.message.message_id, mes.message_id])

async def poster_send_swap_keyboard(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		reply_markup, reaction_with = inline.parse_swap_keyboard(message.text, data.get('channel_id'))
		mes = await bot.send_message(config.TRASH_CHANNEL_ID, 'qwerty', reply_markup=reply_markup)
	except Exception as e:
		print(e)
		await message.answer(templates.error_parse_keyboard)
		return

	if reply_markup is None:
		await message.answer(templates.error_parse_keyboard)
		return

	await state.update_data(reply_markup=reply_markup, reaction_with=reaction_with)
	data = await state.get_data()
	data['dicts'][0]['reply_markup'] = reply_markup
	data['reaction_with'] = reaction_with
	await state.set_state(states.Poster.settingPost)

	try:
		await bot.edit_message_reply_markup(message.from_user.id, data['post_message_id'], reply_markup=reply_markup)
	except Exception as e:
		print(e)

	data['reply_markup'] = mes.reply_markup
	data['hidden_sequel'] = None
	await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	await bot.delete_message(message.from_user.id, data['message_id'][1])
	await bot.delete_message(message.from_user.id, message.message_id)
	await state.update_data(data)
	await state.update_data(message_id=None)


async def poster_swap_text_handler(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Poster.sendText)
	mes = await call.message.answer(templates.poster_swap_text_message, reply_markup=templates.only_back())
	await state.update_data(message_to_delete=[mes.message_id])


async def poster_send_swap_text_handler(message: types.Message, state: FSMContext):
	text = message.html_text
	data = await state.get_data()
	for i in data['dicts']:
		if i['text']:
			i['text'] = ''
	data['dicts'][0]['text'] = text


	channel = Channel.get(id=data.get('channel_id'))

	if len(data['dicts']) > 1:
		reply_markup = None
	else:
		reply_markup = data['dicts'][0]['reply_markup']

	if data['dicts'][0]['type'] == 'text':
		await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['post_message_id'],
									reply_markup=reply_markup)
	else:
		print(data['post_message_id'])
		for i in range(len(data['dicts'])):
			if data['dicts'][i]['text']:
				try:
					await bot.edit_message_caption(message.chat.id, data['post_message_id'] + i, caption='',
												   reply_markup=data['dicts'][0]['reply_markup'])
				except Exception as e:
					pass
		await bot.edit_message_caption(caption=text, chat_id=message.from_user.id, message_id=data['post_message_id'],
									   reply_markup=reply_markup)
	for i in data['message_to_delete']:
		await bot.delete_message(message.from_user.id, i)

	await bot.delete_message(message.from_user.id, message.message_id)
	await state.set_state(states.Poster.settingPost)
	await state.update_data(dicts=data['dicts'], message_to_delete=None)

async def poster_swap_media_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	if data['dicts'][0]['type'] in ['text']:
		await call.message.answer('Недоступно для данного сообщения!')
		return
	await state.set_state(states.Poster.sendMedia)
	# point
	mes = await call.message.answer(templates.poster_swap_media_message, reply_markup=templates.only_back())
	await state.update_data(message_id_delete=mes.message_id, old_data=data, dicts=[], mess=[],
							start_message_id=None)

async def poster_send_swap_media_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if data.get('start_message_id') is None:
		# print(data)
		# print(data['dicts'])
		# if len(data['dicts']) != 0:
		# 	data['text'] = data['dicts'][0]['text']
		data['start_message_id'] = 0
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])
	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)

	if not await next_message_exists(message):
		data = await state.get_data()
		# if data.get('album_message'):
		# 	return
		mess = await send_message_dicts(dicts, message.chat.id)
		p = PostInfo.create()
		mes = await message.answer(templates.album_edit_message,
								   reply_markup=templates.poster_send_post_menu(context=p.id),
								   disable_web_page_preview=True)
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		await bot.delete_message(message.chat.id, data['message_id_delete'])
		old_data = data.get('old_data')
		for i in range(len(old_data['dicts'])):
			try:
				await bot.delete_message(message.chat.id, data['post_message_id'] + i)
			except Exception as e:
				print(e)
		data.pop('old_data')
		await state.set_state(states.Poster.settingPost)
		await state.update_data(data)

		await state.update_data(info=p.id, active=True, post_message_id=post_message_id, album_message=mes.message_id,
								post_message=mess)
		for mes in data.pop('mess'):
			await mes.delete()


async def poster_swap_links_handler(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(states.Poster.sendLink)
	mes = await call.message.answer(templates.poster_swap_links_message, reply_markup=templates.only_back())
	await state.update_data(message_to_delete=[mes.message_id])

async def poster_send_swap_links_handler(message: types.Message, state: FSMContext):
	link = message.text
	data = await state.get_data()
	main_dict = data.get('dicts')[0]
	print(main_dict)
	main_dict['text'] = utils.swap_links_in_text(main_dict['text'], link)
	main_dict['reply_markup'] = utils.swap_links_in_markup(main_dict.get('reply_markup'), link)

	print(data.get('dicts'))
	await utils.send_message_dicts(data.get('dicts'), message.from_user.id)

	mes = await message.answer(templates.album_edit_message,
									   reply_markup=templates.poster_send_post_menu(context=data['info']),
									   disable_web_page_preview=True)

	await state.set_state(states.Poster.settingPost)


async def poster_change_postpone_date_handlers(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(templates.poster_postpone_message, reply_markup=inline.moder_postpone(data))


async def poster_send_time_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(templates.error_parse_time_message)
		return
	await bot.delete_message(message.from_user.id, data['message_id'])
	human_date = parsed['human_date']
	seconds = parsed['seconds']

	channel = Channel.get(id=data['channel_id'])
	channel_id = data['channel_id']
	ch = await bot.get_chat(channel.channel_id)

	p = PostInfo.get(id=data['info'])

	schedule = Schedule.get(channel_id=channel.channel_id)
	admin_id = channel.admin_id

	if schedule.confirm:
		moder_id = schedule.confirm_id if schedule.confirm_id else admin_id
		moder = False
	else:
		moder_id = config.MODERATION_CHANNEL_ID
		moder = True

	dictObject = DictObject.create(owner_id=message.from_user.id,
								   price=p.price,
								   is_advert=True)
	dictObject.save()

	for dict in data['dicts']:
		object = Dict.create(
			object_id=dictObject.id,
			type=dict.get('type'),
			file_id=dict.get('file_id'),
			file_path=dict.get('file_path'),
			text=dict.get('text'),
			reply_markup=utils.create_keyboard(dict.get('reply_markup')),
		)
		object.save()

	manager_placement = ManagerPlacement.create(
		manager_id=message.from_user.id,
		channel_id=channel.channel_id,
		user_id=message.from_user.id,
		admin_id=admin_id,
		dict_object_id=dictObject.id,
		time=seconds + time.time(),
		human_time=human_date,
		price=p.price,
		info=p.id,
		client_name=data['client_name']
	)

	manager_placement.save()

	print(moder_id)

	await utils.send_message_dicts(data['dicts'], moder_id)


	await bot.send_message(moder_id, templates.moder_manager_message(manager_placement, message.from_user, ch), reply_markup=templates.moder_manager_post(manager_placement.id))

	# await message.answer(human_date)

	await state.finish()
	await message.answer('Пост(ы) получен(ы) и отправлен(ы) на согласование', reply_markup=templates.manager_menu())


async def poster_moder_manager_yes(call: types.CallbackQuery, state: FSMContext):
	id = int(call.data.split('$')[1])
	manager_placement = ManagerPlacement.get(id=id)

	manager_placement.is_moderated = True
	manager_placement.save()

	channel = Channel.get(channel_id=manager_placement.channel_id)

	post_time = PostTime.create(
		user_id=manager_placement.manager_id,
		channel_id=channel.id,
		post_id=manager_placement.dict_object_id,
		human_time=manager_placement.human_time,
		time=manager_placement.time
	)

	post_info = PostInfo.get(id=manager_placement.info)
	post_info.post_id=post_time.post_id
	post_info.save()


	ch = await bot.get_chat(manager_placement.channel_id)
	manager = Manager.get(admin_id=manager_placement.manager_id)

	await call.message.delete()
	await bot.send_message(manager_placement.manager_id, templates.moder_manager_post_yes_to_manager(manager_placement, ch, manager),
						   reply_markup=templates.moder_manager_post_yes_to_manager_menu(manager_placement.id))





async def poster_moder_manager_no(call: types.CallbackQuery, state: FSMContext):
	id = int(call.data.split('$')[1])
	manager_placement = ManagerPlacement.get(id=id)

	ch = await bot.get_chat(manager_placement.channel_id)

	await call.message.delete()
	await bot.send_message(manager_placement.manager_id, templates.moder_manager_post_no_to_manager(manager_placement, ch))

async def service_poster_manager_post_paid(call: types.CallbackQuery, state: FSMContext):
	print('something')
	id = int(call.data.split('$')[1])
	manager_placement = ManagerPlacement.get(id=id)

	manager_placement.is_paid = True
	manager_placement.fee_is_paid = False

	manager_placement.save()

	ch = await bot.get_chat(manager_placement.channel_id)
	manager = await bot.get_chat(manager_placement.manager_id)

	url = await manager.get_url()

	channel = Channel.get(channel_id=manager_placement.channel_id)

	await bot.send_message(channel.admin_id, templates.paid_manager_message(manager_placement, url, manager, ch),
						   reply_markup=templates.paid_manager_message_menu(manager_placement.id))


async def poster_manager_post_paid(call: types.CallbackQuery, state: FSMContext):
	await service_poster_manager_post_paid(call, state)
	await call.message.answer("Админ получил уведомление об оплате")
	await call.message.delete()


async def poster_manager_post_true_paid(call: types.CallbackQuery, state: FSMContext):
	id = int(call.data.split('$')[1])
	manager_placement = ManagerPlacement.get(id=id)

	manager_placement.is_admin_paid = True
	manager_placement.save()

	await call.message.delete()


def register_poster_handlers(dp: Dispatcher):
	dp.register_message_handler(poster_handler, text=templates.make_post_button, state='*')
	dp.register_message_handler(cancel_poster_handler, text=templates.cancel_button, state=states.Poster)
	dp.register_message_handler(send_client_name_handler, content_types=['text'], state=states.Poster.sendClientName)

	dp.register_callback_query_handler(poster_choose_channel_handler, text_startswith="poster_choose_channel", state=states.Poster.sendChannel)

	dp.register_callback_query_handler(poster_swap_comments_handler, text="swap_comments", state=states.Poster.settingPost)
	dp.register_callback_query_handler(poster_change_price_handler, text='edit_price', state=states.Poster.settingPost)
	dp.register_message_handler(poster_send_changed_price_handler, content_types=['text'], state=states.Poster.sendPrice)
	dp.register_callback_query_handler(back_poster_change_price_handler, text='back',
									   state=[
										   states.Poster.sendPrice,
										   states.Poster.sendKeyboard,
										   states.Poster.sendText,
										   states.Poster.sendMedia,
										   states.Poster.sendLink
									    ]
									   )

	dp.register_callback_query_handler(poster_postpone_back_handler, text='back', state=states.Poster.sendTime)

	dp.register_callback_query_handler(poster_swap_keyboard, text='swap_keyboard', state=states.Poster.settingPost)
	dp.register_message_handler(poster_send_swap_keyboard, content_types=['text'], state=states.Poster.sendKeyboard)

	dp.register_callback_query_handler(poster_swap_text_handler, text='edit_text', state=states.Poster.settingPost)
	dp.register_message_handler(poster_send_swap_text_handler, content_types=['text'], state=states.Poster.sendText)

	dp.register_callback_query_handler(poster_swap_media_handler, text='edit_media', state=states.Poster.settingPost)
	dp.register_message_handler(poster_send_swap_media_handler, state=states.Poster.sendMedia, content_types=types.ContentTypes.ANY)


	dp.register_callback_query_handler(poster_swap_links_handler, text='swap_links', state=states.Poster.settingPost)
	dp.register_message_handler(poster_send_swap_links_handler, content_types=['text'], state=states.Poster.sendLink)


	dp.register_callback_query_handler(poster_cancel, text='back_post', state=states.Poster)
	dp.register_callback_query_handler(poster_next_post, text='next_post', state=states.Poster)

	dp.register_callback_query_handler(poster_change_postpone_date_handlers,
									   state=states.Poster.sendTime, text_startswith='postpone_date$')
	dp.register_message_handler(poster_send_time_handler, content_types=['text'], state=states.Poster.sendTime)


	dp.register_callback_query_handler(poster_moder_manager_yes, text_startswith="moder_manager_post_yes", state="*")
	dp.register_callback_query_handler(poster_moder_manager_no, text_startswith="moder_manager_post_no", state="*")

	dp.register_callback_query_handler(poster_manager_post_paid, text_startswith="manager_post_paid", state="*")

	dp.register_callback_query_handler(poster_manager_post_true_paid, text_startswith="manager_post_true_paid", state="*")




	dp.register_message_handler(send_post_poster_handler, lambda message: message.chat.type == 'private', state=states.Poster.sendPost, content_types=types.ContentTypes.ANY)

