object frmMain: TfrmMain
  Left = 0
  Top = 0
  Caption = 'Cognitive OSINT Engine - B2B Intelligence'
  ClientHeight = 750
  ClientWidth = 1200
  Color = 16382457
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -14
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnClose = FormClose
  OnCreate = FormCreate
  TextHeight = 19
  object pnlLogin: TPanel
    Left = 0
    Top = 0
    Width = 1200
    Height = 750
    Align = alClient
    BevelOuter = bvNone
    Color = 16382457
    ParentBackground = False
    TabOrder = 0
    object pnlLoginBox: TPanel
      Left = 400
      Top = 200
      Width = 400
      Height = 350
      BevelOuter = bvNone
      Color = clWhite
      ParentBackground = False
      TabOrder = 0
      object lblLoginTitle: TLabel
        Left = 0
        Top = 40
        Width = 400
        Height = 30
        Alignment = taCenter
        AutoSize = False
        Caption = 'G'#252'venli Sisteme Giri'#351
        Font.Charset = DEFAULT_CHARSET
        Font.Color = 3026478
        Font.Height = -21
        Font.Name = 'Segoe UI Semibold'
        Font.Style = []
        ParentFont = False
      end
      object edtUsername: TEdit
        Left = 50
        Top = 110
        Width = 300
        Height = 33
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -16
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        TabOrder = 0
        TextHint = '  Kullan'#305'c'#305' Ad'#305
      end
      object edtPassword: TEdit
        Left = 50
        Top = 165
        Width = 300
        Height = 33
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -16
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        PasswordChar = '*'
        TabOrder = 1
        TextHint = '  '#350'ifre'
      end
      object btnLogin: TButton
        Left = 50
        Top = 230
        Width = 140
        Height = 45
        Caption = 'Giri'#351' Yap'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -15
        Font.Name = 'Segoe UI Semibold'
        Font.Style = []
        ParentFont = False
        TabOrder = 2
        OnClick = btnLoginClick
      end
      object btnRegister: TButton
        Left = 210
        Top = 230
        Width = 140
        Height = 45
        Caption = 'Kay'#305't Ol'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -15
        Font.Name = 'Segoe UI Semibold'
        Font.Style = []
        ParentFont = False
        TabOrder = 3
        OnClick = btnRegisterClick
      end
    end
  end
  object pgcMain: TPageControl
    Left = 0
    Top = 0
    Width = 1200
    Height = 750
    ActivePage = tsRecherche
    Align = alClient
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -15
    Font.Name = 'Segoe UI Semibold'
    Font.Style = []
    ParentFont = False
    TabOrder = 1
    Visible = False
    object tsRecherche: TTabSheet
      Caption = '   Ara & Ke'#351'fet   '
      object pnlFiltreler: TPanel
        Left = 0
        Top = 0
        Width = 280
        Height = 718
        Align = alLeft
        BevelOuter = bvNone
        Color = 15724527
        ParentBackground = False
        TabOrder = 0
        object lblFiltreBaslik: TLabel
          Left = 20
          Top = 25
          Width = 240
          Height = 25
          AutoSize = False
          Caption = 'Filtreleme Se'#231'enekleri'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = 3026478
          Font.Height = -17
          Font.Name = 'Segoe UI Bold'
          Font.Style = []
          ParentFont = False
        end
        object lblBotBaslik: TLabel
          Left = 20
          Top = 430
          Width = 240
          Height = 25
          AutoSize = False
          Caption = 'Canl'#305' Veri Toplama'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = 3026478
          Font.Height = -17
          Font.Name = 'Segoe UI Bold'
          Font.Style = []
          ParentFont = False
        end
        object edtSehir: TEdit
          Left = 20
          Top = 75
          Width = 240
          Height = 28
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -15
          Font.Name = 'Segoe UI'
          Font.Style = []
          ParentFont = False
          TabOrder = 0
          TextHint = '  '#350'ehir (Orn: '#304'stanbul)'
        end
        object cmbSektor: TComboBox
          Left = 20
          Top = 125
          Width = 240
          Height = 28
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -15
          Font.Name = 'Segoe UI'
          Font.Style = []
          ParentFont = False
          TabOrder = 1
          TextHint = '  Sekt'#246'r (Orn: Yaz'#305'l'#305'm)'
        end
        object edtUnvan: TEdit
          Left = 20
          Top = 175
          Width = 240
          Height = 28
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -15
          Font.Name = 'Segoe UI'
          Font.Style = []
          ParentFont = False
          TabOrder = 6
          TextHint = '  '#220'nvan / Pozisyon (Orn: CTO)'
        end
        object cmbCalisanSayisi: TComboBox
          Left = 20
          Top = 225
          Width = 240
          Height = 28
          Style = csDropDownList
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -15
          Font.Name = 'Segoe UI'
          Font.Style = []
          ParentFont = False
          TabOrder = 2
        end
        object chkSadeceYatirimAlanlar: TCheckBox
          Left = 20
          Top = 280
          Width = 240
          Height = 20
          Caption = 'Sadece Yat'#305'r'#305'm Alanlar'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -15
          Font.Name = 'Segoe UI'
          Font.Style = []
          ParentFont = False
          TabOrder = 3
        end
        object btnAra: TButton
          Left = 20
          Top = 330
          Width = 240
          Height = 45
          Caption = 'Veritaban'#305'nda Ara'
          TabOrder = 4
          OnClick = btnAraClick
        end
        object btnTaramaBaslat: TButton
          Left = 20
          Top = 470
          Width = 240
          Height = 55
          Caption = 'OSINT Botunu Tetikle'
          TabOrder = 5
          OnClick = btnTaramaBaslatClick
        end
      end
      object dbgSonuclar: TDBGrid
        Left = 280
        Top = 0
        Width = 912
        Height = 715
        Align = alClient
        BorderStyle = bsNone
        Color = clWhite
        DataSource = dsSonuclar
        DrawingStyle = gdsClassic
        FixedColor = clWhite
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -13
        Font.Name = 'Segoe UI'
        Font.Style = []
        Options = [dgTitles, dgIndicator, dgColumnResize, dgColLines, dgRowLines, dgTabs, dgRowSelect, dgConfirmDelete, dgCancelOnExit, dgTitleClick, dgTitleHotTrack]
        ParentFont = False
        TabOrder = 1
        TitleFont.Charset = DEFAULT_CHARSET
        TitleFont.Color = clWindowText
        TitleFont.Height = -15
        TitleFont.Name = 'Segoe UI Semibold'
        TitleFont.Style = []
        OnDblClick = dbgSonuclarDblClick
      end
    end
    object tsIstatistik: TTabSheet
      Caption = '   Sekt'#246'rel '#304'statistikler   '
      ImageIndex = 1
      object pnlIstatistikTop: TPanel
        Left = 0
        Top = 0
        Width = 1192
        Height = 80
        Align = alTop
        BevelOuter = bvNone
        Color = clWhite
        ParentBackground = False
        TabOrder = 0
        object btnAnalizGetir: TButton
          Left = 30
          Top = 20
          Width = 220
          Height = 40
          Caption = 'Raporu Getir'
          TabOrder = 0
          OnClick = btnAnalizGetirClick
        end
      end
      object mmoIstatistik: TMemo
        Left = 0
        Top = 80
        Width = 1192
        Height = 638
        Align = alClient
        Color = 16382457
        Font.Charset = DEFAULT_CHARSET
        Font.Color = 3026478
        Font.Height = -16
        Font.Name = 'Consolas'
        Font.Style = []
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssVertical
        TabOrder = 1
      end
    end
    object tsLoglar: TTabSheet
      Caption = '   Sistem Loglar'#305'   '
      ImageIndex = 2
      object mmoLoglar: TMemo
        Left = 0
        Top = 0
        Width = 1192
        Height = 718
        Align = alClient
        Color = 1184274
        Font.Charset = ANSI_CHARSET
        Font.Color = clLime
        Font.Height = -15
        Font.Name = 'Consolas'
        Font.Style = []
        ParentFont = False
        ReadOnly = True
        ScrollBars = ssBoth
        TabOrder = 0
      end
    end
  end
  object RestClient: TRESTClient
    BaseURL = 'http://localhost:8000/api/v1'
    Params = <>
    SynchronizedEvents = False
    Left = 56
    Top = 536
  end
  object RestRequest: TRESTRequest
    Client = RestClient
    Params = <>
    Response = RestResponse
    SynchronizedEvents = False
    Left = 144
    Top = 536
  end
  object RestResponse: TRESTResponse
    Left = 232
    Top = 536
  end
  object RestAdapter: TRESTResponseDataSetAdapter
    Dataset = MemTableSonuclar
    FieldDefs = <>
    Response = RestResponse
    Left = 56
    Top = 592
  end
  object MemTableSonuclar: TFDMemTable
    FetchOptions.AssignedValues = [evMode]
    FetchOptions.Mode = fmAll
    ResourceOptions.AssignedValues = [rvSilentMode]
    ResourceOptions.SilentMode = True
    UpdateOptions.AssignedValues = [uvCheckRequired, uvAutoCommitUpdates]
    UpdateOptions.CheckRequired = False
    UpdateOptions.AutoCommitUpdates = True
    Left = 144
    Top = 592
  end
  object dsSonuclar: TDataSource
    DataSet = MemTableSonuclar
    Left = 232
    Top = 592
  end
  object RestReqStats: TRESTRequest
    Client = RestClient
    Params = <>
    Response = RestResStats
    SynchronizedEvents = False
    Left = 144
    Top = 648
  end
  object RestResStats: TRESTResponse
    Left = 232
    Top = 648
  end
end
