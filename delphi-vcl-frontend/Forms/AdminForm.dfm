object FrmAdmin: TFrmAdmin
  Left = 0
  Top = 0
  Caption = 'Yonetim Paneli'
  ClientHeight = 620
  ClientWidth = 980
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poMainFormCenter
  TextHeight = 15
  object LblTitle: TLabel
    Left = 24
    Top = 16
    Width = 137
    Height = 28
    Caption = 'Yonetim Paneli'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblUsers: TLabel
    Left = 24
    Top = 112
    Width = 32
    Height = 15
    Caption = 'Kullanicilar'
  end
  object LblLogs: TLabel
    Left = 500
    Top = 112
    Width = 28
    Height = 15
    Caption = 'Sistem Loglari'
  end
  object LblStatus: TLabel
    Left = 24
    Top = 592
    Width = 43
    Height = 15
    Caption = 'Durum:'
  end
  object BtnLoadUsers: TButton
    Left = 24
    Top = 64
    Width = 140
    Height = 32
    Caption = 'Kullanicilari Yukle'
    TabOrder = 0
    OnClick = BtnLoadUsersClick
  end
  object BtnLoadLogs: TButton
    Left = 172
    Top = 64
    Width = 140
    Height = 32
    Caption = 'Loglari Yukle'
    TabOrder = 1
    OnClick = BtnLoadLogsClick
  end
  object BtnClose: TButton
    Left = 320
    Top = 64
    Width = 120
    Height = 32
    Caption = 'Kapat'
    TabOrder = 2
    OnClick = BtnCloseClick
  end
  object MemoUsers: TMemo
    Left = 24
    Top = 136
    Width = 452
    Height = 440
    ScrollBars = ssVertical
    TabOrder = 3
  end
  object MemoLogs: TMemo
    Left = 500
    Top = 136
    Width = 452
    Height = 440
    ScrollBars = ssVertical
    TabOrder = 4
  end
end
