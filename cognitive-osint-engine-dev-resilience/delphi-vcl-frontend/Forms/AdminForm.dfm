object FrmAdmin: TAdminForm
  Left = 0
  Top = 0
  Caption = 'Admin Panel'
  ClientHeight = 760
  ClientWidth = 1220
  Color = clWhite
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -13
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poMainFormCenter
  TextHeight = 17
  object LblTitle: TLabel
    Left = 20
    Top = 16
    Width = 139
    Height = 33
    Caption = 'Admin Paneli'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = $00A0522D
    Font.Height = -24
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object PnlLeft: TPanel
    Left = 0
    Top = 54
    Width = 390
    Height = 706
    Align = alLeft
    BevelOuter = bvRaised
    Color = $00F8FAFC
    ParentBackground = False
    TabOrder = 0
    object LblUsers: TLabel
      Left = 16
      Top = 12
      Width = 94
      Height = 17
      Caption = 'Kullanicilar'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = $00404040
      Font.Height = -13
      Font.Name = 'Segoe UI'
      Font.Style = [fsBold]
      ParentFont = False
    end
    object GridUsers: TStringGrid
      Left = 12
      Top = 40
      Width = 366
      Height = 654
      Color = clWhite
      ColCount = 5
      DefaultRowHeight = 24
      FixedCols = 0
      FixedColor = clActiveCaption
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'Segoe UI'
      Font.Style = []
      Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRowSelect, goThumbTracking]
      RowCount = 2
      TabOrder = 0
      ColWidths = (
        48
        120
        135
        70
        100)
    end
  end
  object SplitterMain: TSplitter
    Left = 390
    Top = 54
    Width = 8
    Height = 706
    Align = alLeft
  end
  object PnlRight: TPanel
    Left = 398
    Top = 54
    Width = 822
    Height = 706
    Align = alClient
    BevelOuter = bvRaised
    Color = $00F8FAFC
    ParentBackground = False
    TabOrder = 1
    object PnlHistory: TPanel
      Left = 1
      Top = 1
      Width = 820
      Height = 340
      Align = alTop
      BevelOuter = bvNone
      Color = clWhite
      ParentBackground = False
      TabOrder = 0
      object LblHistory: TLabel
        Left = 16
        Top = 12
        Width = 90
        Height = 17
        Caption = 'Arama Gecmisi'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = $00404040
        Font.Height = -13
        Font.Name = 'Segoe UI'
        Font.Style = [fsBold]
        ParentFont = False
      end
      object GridSearchHistory: TStringGrid
        Left = 12
        Top = 40
        Width = 796
        Height = 288
        Color = clWhite
        ColCount = 5
        DefaultRowHeight = 24
        FixedCols = 0
        FixedColor = clActiveCaption
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRowSelect, goThumbTracking]
        RowCount = 2
        TabOrder = 0
        ColWidths = (
          95
          250
          140
          90
          130)
      end
    end
    object SplitterRight: TSplitter
      Left = 1
      Top = 341
      Width = 820
      Height = 8
      Cursor = crVSplit
      Align = alTop
    end
    object PnlCompanies: TPanel
      Left = 1
      Top = 349
      Width = 820
      Height = 356
      Align = alClient
      BevelOuter = bvNone
      Color = clWhite
      ParentBackground = False
      TabOrder = 1
      object LblCompanies: TLabel
        Left = 16
        Top = 12
        Width = 63
        Height = 17
        Caption = 'Sirketler'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = $00404040
        Font.Height = -13
        Font.Name = 'Segoe UI'
        Font.Style = [fsBold]
        ParentFont = False
      end
      object GridCompanies: TStringGrid
        Left = 12
        Top = 40
        Width = 796
        Height = 304
        Color = clWhite
        ColCount = 10
        DefaultRowHeight = 24
        FixedCols = 0
        FixedColor = clActiveCaption
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -12
        Font.Name = 'Segoe UI'
        Font.Style = []
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRowSelect, goThumbTracking]
        RowCount = 2
        TabOrder = 0
        ColWidths = (
          45
          130
          85
          75
          65
          120
          110
          95
          110
          120)
      end
    end
  end
end
