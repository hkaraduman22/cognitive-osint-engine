object FrmMain: TFrmMain
  Left = 0
  Top = 0
  Caption = 'OSINT Kontrol Paneli'
  ClientHeight = 520
  ClientWidth = 900
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  OnClose = FormClose
  TextHeight = 15
  object PnlTop: TPanel
    Left = 0
    Top = 0
    Width = 900
    Height = 97
    Align = alTop
    BevelOuter = bvLowered
    Color = clWhite
    ParentBackground = False
    TabOrder = 0
    object LblTitle: TLabel
      Left = 24
      Top = 12
      Width = 182
      Height = 28
      Caption = 'OSINT Kontrol Paneli'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -21
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object LblWelcome: TLabel
      Left = 24
      Top = 48
      Width = 70
      Height = 15
      Caption = 'Hos geldiniz'
    end
    object LblSession: TLabel
      Left = 24
      Top = 69
      Width = 102
      Height = 15
      Caption = 'JWT session durumu'
    end
  end
  object BtnSearch: TButton
    Left = 24
    Top = 128
    Width = 200
    Height = 44
    Caption = 'Arama'
    TabOrder = 1
    OnClick = BtnSearchClick
  end
  object BtnResults: TButton
    Left = 24
    Top = 184
    Width = 200
    Height = 44
    Caption = 'Sonuclar'
    TabOrder = 2
    OnClick = BtnResultsClick
  end
  object BtnHistory: TButton
    Left = 24
    Top = 240
    Width = 200
    Height = 44
    Caption = 'Arama Gecmisi'
    TabOrder = 3
    OnClick = BtnHistoryClick
  end
  object BtnAdmin: TButton
    Left = 24
    Top = 296
    Width = 200
    Height = 44
    Caption = 'Yonetim'
    TabOrder = 4
    OnClick = BtnAdminClick
  end
  object BtnLogout: TButton
    Left = 24
    Top = 352
    Width = 200
    Height = 44
    Caption = 'Cikis Yap'
    TabOrder = 5
    OnClick = BtnLogoutClick
  end
  object LblLastQuery: TLabel
    Left = 24
    Top = 416
    Width = 145
    Height = 15
    Caption = 'Henuz arama yapilmadi.'
  end
end
